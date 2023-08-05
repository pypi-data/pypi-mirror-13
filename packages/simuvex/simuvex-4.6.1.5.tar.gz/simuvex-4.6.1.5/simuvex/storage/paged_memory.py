import collections
import cooldict
import claripy
import cffi
import cle

from ..s_errors import SimMemoryError
from .. import s_options as options
from .memory_object import SimMemoryObject

_ffi = cffi.FFI()

import logging
l = logging.getLogger('simuvex.storage.paged_memory')

#pylint:disable=unidiomatic-typecheck

class SimPagedMemory(collections.MutableMapping):
    def __init__(self, backer=None, pages=None, name_mapping=None, hash_mapping=None, page_size=None):
        self._backer = { } if backer is None else backer
        self._pages = { } if pages is None else pages
        self._page_size = 0x1000 if page_size is None else page_size
        self.state = None

        # reverse mapping
        self._name_mapping = cooldict.BranchingDict() if name_mapping is None else name_mapping
        self._hash_mapping = cooldict.BranchingDict() if hash_mapping is None else hash_mapping
        self._updated_mappings = set()

    def __getstate__(self):
        return {
            '_backer': self._backer,
            '_pages': self._pages,
            '_page_size': self._page_size,
            'state': self.state,
            '_name_mapping': self._name_mapping,
            '_hash_mapping': self._hash_mapping,
        }

    def __setstate__(self, s):
        self.__dict__.update(s)

    def branch(self):
        new_pages = { k:v.branch() for k,v in self._pages.iteritems() }
        new_name_mapping = self._name_mapping.branch() if options.REVERSE_MEMORY_NAME_MAP in self.state.options else self._name_mapping
        new_hash_mapping = self._hash_mapping.branch() if options.REVERSE_MEMORY_HASH_MAP in self.state.options else self._hash_mapping

        m = SimPagedMemory(backer=self._backer,
                           pages=new_pages,
                           page_size=self._page_size,
                           name_mapping=new_name_mapping,
                           hash_mapping=new_hash_mapping)
        return m

    def __getitem__(self, addr):
        page_num = addr / self._page_size
        page_idx = addr % self._page_size
        #print "GET", addr, page_num, page_idx

        if page_num not in self._pages:
            self._initialize_page(page_num)
        return self._pages[page_num][page_idx]

    def __setitem__(self, addr, v):
        page_num = addr / self._page_size
        page_idx = addr % self._page_size
        #print "SET", addr, page_num, page_idx

        self._update_mappings(addr, v.object)
        if page_num not in self._pages:
            self._initialize_page(page_num)
        self._pages[page_num][page_idx] = v
        #print "...",id(self._pages[page_num])

    def __delitem__(self, addr):
        raise Exception("For performance reasons, deletion is not supported. Contact Yan if this needs to change.")
        # Specifically, the above is for two reasons:
        #
        #     1. deleting stuff out of memory doesn't make sense
        #     2. if the page throws a key error, the backer dict is accessed. Thus, deleting things would simply
        #        change them back to what they were in the backer dict

        #page_num = addr / self._page_size
        #page_idx = addr % self._page_size
        ##print "DEL", addr, page_num, page_idx

        #if page_num not in self._pages:
        #     self._pages[page_num] = cooldict.BranchingDict(d=self._backer)
        #del self._pages[page_num][page_idx]

    def load_bytes(self, addr, num_bytes):
        missing = [ ]
        the_bytes = { }

        l.debug("Reading from memory at %#x", addr)
        i = 0
        while i < num_bytes:
            actual_addr = addr + i
            page_num = actual_addr/self._page_size

            try:
                b = self[actual_addr]
                the_bytes[i] = b

                page = self._pages[page_num]
                if page._sinkholed and len(page) == 0:
                    i += self._page_size - actual_addr%self._page_size
                else:
                    i += 1
            except KeyError: # this one is from missing bytes
                missing.append(i)
                if len(self._pages[page_num]) == 0: # the whole page is missing!
                    i += self._page_size - actual_addr%self._page_size
                else:
                    i += 1

        l.debug("... %d found, %d missing", len(the_bytes), len(missing))
        return the_bytes, missing

    def store_memory_object(self, mo, overwrite=True):
        '''
        This function optimizes a large store by storing a single reference to
        the SimMemoryObject instead of one for each byte.

        @param memory_object: the memory object to store
        '''

        self._update_range_mappings(mo.base, mo.object, mo.length)

        mo_start = mo.base
        mo_end = mo.base + mo.length
        page_start = mo_start - mo_start%self._page_size
        page_end = mo_end + (self._page_size - mo_end%self._page_size) if mo_end % self._page_size else mo_end
        pages = [ b for b in range(page_start, page_end, self._page_size) ]

        for p in pages:
            page_num = p / self._page_size
            if page_num not in self._pages:
                self._initialize_page(page_num)
            page = self._pages[page_num]

            #print (mo.base, mo.length), (p, p + self._page_size)

            if mo.base <= p and mo.base + mo.length >= p + self._page_size:
                # takes up the whole page
                page.sinkhole(mo, wipe=overwrite)
            else:
                for a in range(max(mo.base, p), min(mo.base+mo.length, p+self._page_size)):
                    if overwrite or a%self._page_size not in page:
                        page[a%self._page_size] = mo

    def _initialize_page(self, n):
        new_page = cooldict.SinkholeCOWDict()
        self._pages[n] = new_page

        new_page_addr = n*self._page_size
        if self._backer is None:
            pass
        elif isinstance(self._backer, cle.Clemory):
            # first, find the right clemory backer
            for addr, backer in self._backer.cbackers:
                start_backer = new_page_addr - addr

                if start_backer < 0 and abs(start_backer) > self._page_size:
                    continue
                if start_backer > len(backer):
                    continue

                snip_start = max(0, start_backer)
                write_start = max(new_page_addr, addr + snip_start)
                write_size = self._page_size - write_start%self._page_size

                #print hex(addr), hex(snip_start), write_size, hex(write_start)
                #import ipdb; ipdb.set_trace()

                snip = _ffi.buffer(backer)[snip_start:snip_start+write_size]
                mo = SimMemoryObject(claripy.BVV(snip), write_start)
                self.store_memory_object(mo)
        elif len(self._backer) < self._page_size:
            for i in self._backer:
                if new_page_addr <= i and i <= new_page_addr + self._page_size:
                    self.store_memory_object(SimMemoryObject(claripy.BVV(self._backer[i]), i))
        elif len(self._backer) > self._page_size:
            for i in range(self._page_size):
                try:
                    self.store_memory_object(SimMemoryObject(claripy.BVV(self._backer[i]), new_page_addr+i))
                except KeyError:
                    pass

    def __contains__(self, addr):
        try:
            self.__getitem__(addr)
            return True
        except KeyError:
            return False

    def __iter__(self):
        for k in self._backer:
            yield k
        for p in self._pages:
            if not self._pages[p]._sinkholed:
                for a in self._pages[p]:
                    yield p*self._page_size + a
            else:
                for a in range(self._page_size):
                    yield p*self._page_size + a

    def __len__(self):
        return sum((len(v) if not self._pages._sinkholed else self._page_size) for v in self._pages.itervalues())

    def changed_bytes(self, other):
        '''
        Gets the set of changed bytes between self and other.

        @param other: the other SimPagedMemory
        @returns a set of differing bytes
        '''
        if self._page_size != other._page_size:
            raise SimMemoryError("SimPagedMemory page sizes differ. This is asking for disaster.")

        our_pages = set(self._pages.keys())
        their_pages = set(other._pages.keys())
        their_additions = their_pages - our_pages
        our_additions = our_pages - their_pages
        common_pages = our_pages & their_pages

        candidates = set()
        for p in their_additions:
            candidates.update([ (p*self._page_size)+i for i in other._pages[p] ])
        for p in our_additions:
            candidates.update([ (p*self._page_size)+i for i in self._pages[p] ])

        for p in common_pages:
            our_page = self._pages[p]
            their_page = other._pages[p]

            common_ancestor = our_page.common_ancestor(their_page)
            if common_ancestor == None:
                our_changes, our_deletions = set(our_page.iterkeys()), set()
                their_changes, their_deletions = set(their_page.iterkeys()), set()
            else:
                our_changes, our_deletions = our_page.changes_since(common_ancestor)
                their_changes, their_deletions = their_page.changes_since(common_ancestor)

            if our_page._sinkholed or their_page._sinkholed and our_page._sinkhole_value is not their_page._sinkhole_value:
                sinkhole_changes = set(range(self._page_size)) - set(their_page.iterkeys()) - set(our_page.iterkeys())
            else:
                sinkhole_changes = set()


            candidates.update([ (p*self._page_size)+i for i in our_changes | our_deletions | their_changes | their_deletions | sinkhole_changes ])

        #both_changed = our_changes & their_changes
        #ours_changed_only = our_changes - both_changed
        #theirs_changed_only = their_changes - both_changed
        #both_deleted = their_deletions & our_deletions
        #ours_deleted_only = our_deletions - both_deleted
        #theirs_deleted_only = their_deletions - both_deleted

        differences = set()
        for c in candidates:
            if c not in self and c in other:
                differences.add(c)
            elif c in self and c not in other:
                differences.add(c)
            else:
                if type(self[c]) is not SimMemoryObject:
                    self[c] = SimMemoryObject(self.state.se.BVV(ord(self[c]), 8), c)
                if type(other[c]) is not SimMemoryObject:
                    other[c] = SimMemoryObject(self.state.se.BVV(ord(other[c]), 8), c)
                if c in self and self[c] != other[c]:
                    # Try to see if the bytes are equal
                    self_byte = self[c].bytes_at(c, 1)
                    other_byte = other[c].bytes_at(c, 1)
                    if not self_byte is other_byte:
                        #l.debug("%s: offset %x, two different bytes %s %s from %s %s", self.id, c,
                        #        self_byte, other_byte,
                        #        self[c].object.model, other[c].object.model)
                        differences.add(c)
                else:
                    # this means the byte is in neither memory
                    pass

        return differences

    #
    # Memory object management
    #

    def replace_memory_object(self, old, new_content):
        '''
        Replaces the memory object 'old' with a new memory object containing
        'new_content'.

            @param old: a SimMemoryObject (i.e., one from memory_objects_for_hash() or
                        memory_objects_for_name())
            @param new_content: the content (claripy expression) for the new memory object
        '''

        if old.object.size() != new_content.size():
            raise SimMemoryError("memory objects can only be replaced by the same length content")

        new = SimMemoryObject(new_content, old.base)
        for b in range(old.base, old.base+old.length):
            try:
                here = self[b]
                if here is not old:
                    continue

                if isinstance(new.object, claripy.ast.BV):
                    self._update_mappings(b, new.object)
                self[b] = new
            except KeyError:
                pass

    def replace_all(self, old, new):
        '''
        Replaces all instances of expression old with expression new.

            @param old: a claripy expression. Must contain at least one named variable (to make
                        to make it possible to use the name index for speedup)
            @param new: the new variable to replace it with
        '''

        if options.REVERSE_MEMORY_NAME_MAP not in self.state.options:
            raise SimMemoryError("replace_all is not doable without a reverse name mapping. Please add simuvex.o.REVERSE_MEMORY_NAME_MAP to the state options")

        if not isinstance(old, claripy.ast.BV) or not isinstance(new, claripy.ast.BV):
            raise SimMemoryError("old and new arguments to replace_all() must be claripy.BV objects")

        if len(old.variables) == 0:
            raise SimMemoryError("old argument to replace_all() must have at least one named variable")

        # Compute an intersection between sets of memory objects for each unique variable name. The eventual memory
        # object set contains all memory objects that we should update.
        memory_objects = None
        for v in old.variables:
            if memory_objects is None:
                memory_objects = self.memory_objects_for_name(v)
            elif len(memory_objects) == 0:
                # It's a set and it's already empty
                # there is no way for it to go back...
                break
            else:
                memory_objects &= self.memory_objects_for_name(v)

        replaced_objects_cache = { }
        for mo in memory_objects:
            replaced_object = None

            if mo.object in replaced_objects_cache:
                if mo.object is not replaced_objects_cache[mo.object]:
                    replaced_object = replaced_objects_cache[mo.object]

            else:
                replaced_object = mo.object.replace(old, new)
                replaced_objects_cache[mo.object] = replaced_object
                if mo.object is replaced_object:
                    # The replace does not really occur
                    replaced_object = None

            if replaced_object is not None:
                self.replace_memory_object(mo, replaced_object)

    #
    # Mapping bullshit
    #

    def _mark_updated_mapping(self, d, m):
        if m in self._updated_mappings:
            return

        if options.REVERSE_MEMORY_HASH_MAP not in self.state.options and d is self._hash_mapping:
            #print "ABORTING FROM HASH"
            return
        if options.REVERSE_MEMORY_NAME_MAP not in self.state.options and d is self._name_mapping:
            #print "ABORTING FROM NAME"
            return
        #print m
        #SimSymbolicMemory.wtf += 1
        #print SimSymbolicMemory.wtf

        try:
            d[m] = set(d[m])
        except KeyError:
            d[m] = set()
        self._updated_mappings.add(m)

    def _update_range_mappings(self, actual_addr, cnt, size):
        if not (options.REVERSE_MEMORY_NAME_MAP in self.state.options or
                options.REVERSE_MEMORY_HASH_MAP in self.state.options):
            return

        for i in range(actual_addr, actual_addr+size):
            self._update_mappings(i, cnt)

    def _update_mappings(self, actual_addr, cnt):
        if not (options.REVERSE_MEMORY_NAME_MAP in self.state.options or
                options.REVERSE_MEMORY_HASH_MAP in self.state.options):
            return

        if (options.REVERSE_MEMORY_HASH_MAP not in self.state.options) and \
                len(self.state.se.variables(cnt)) == 0:
           return

        l.debug("Updating mappings at address 0x%x", actual_addr)

        try:
            old_obj = self[actual_addr]
            l.debug("... removing old mappings")

            # remove this address for the old variables
            old_obj = self[actual_addr]
            if isinstance(old_obj, SimMemoryObject):
                old_obj = old_obj.object

            if isinstance(old_obj, claripy.ast.BV):
                if options.REVERSE_MEMORY_NAME_MAP in self.state.options:
                    var_set = self.state.se.variables(old_obj)
                    for v in var_set:
                        self._mark_updated_mapping(self._name_mapping, v)
                        self._name_mapping[v].discard(actual_addr)
                        if len(self._name_mapping[v]) == 0:
                            self._name_mapping.pop(v, None)

                if options.REVERSE_MEMORY_HASH_MAP in self.state.options:
                    h = hash(old_obj)
                    self._mark_updated_mapping(self._hash_mapping, h)
                    self._hash_mapping[h].discard(actual_addr)
                    if len(self._hash_mapping[h]) == 0:
                        self._hash_mapping.pop(h, None)
        except KeyError:
            pass

        l.debug("... adding new mappings")
        if options.REVERSE_MEMORY_NAME_MAP in self.state.options:
            # add the new variables to the mapping
            var_set = self.state.se.variables(cnt)
            for v in var_set:
                self._mark_updated_mapping(self._name_mapping, v)
                if v not in self._name_mapping:
                    self._name_mapping[v] = set()
                self._name_mapping[v].add(actual_addr)

        if options.REVERSE_MEMORY_HASH_MAP in self.state.options:
            # add the new variables to the hash->addrs mapping
            h = hash(cnt)
            self._mark_updated_mapping(self._hash_mapping, h)
            if h not in self._hash_mapping:
                self._hash_mapping[h] = set()
            self._hash_mapping[h].add(actual_addr)

    def addrs_for_name(self, n):
        '''
        Returns addresses that contain expressions that contain a variable
        named n.
        '''
        if n not in self._name_mapping:
            return

        self._mark_updated_mapping(self._name_mapping, n)

        to_discard = set()
        for e in self._name_mapping[n]:
            try:
                if n in self[e].object.variables: yield e
                else: to_discard.add(e)
            except KeyError:
                to_discard.add(e)
        self._name_mapping[n] -= to_discard

    def addrs_for_hash(self, h):
        '''
        Returns addresses that contain expressions that contain a variable
        with the hash of h.
        '''
        if h not in self._hash_mapping:
            return

        self._mark_updated_mapping(self._hash_mapping, h)

        to_discard = set()
        for e in self._hash_mapping[h]:
            try:
                if h == hash(self[e].object): yield e
                else: to_discard.add(e)
            except KeyError:
                to_discard.add(e)
        self._hash_mapping[h] -= to_discard

    def memory_objects_for_name(self, n):
        '''
        Returns a set of SimMemoryObjects that contain expressions that contain a variable
        with the name of n. This is useful for replacing those values, in one fell swoop,
        with replace_memory_object(), even if they've been partially overwritten.
        '''
        return set([ self[i] for i in self.addrs_for_name(n)])

    def memory_objects_for_hash(self, n):
        '''
        Returns a set of SimMemoryObjects that contain expressions that contain a variable
        with the hash of h. This is useful for replacing those values, in one fell swoop,
        with replace_memory_object(), even if they've been partially overwritten.
        '''
        return set([ self[i] for i in self.addrs_for_hash(n)])

