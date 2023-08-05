# cython: profile=True
# cython: cdivision=True
# cython: infer_types=True
from libc.string cimport memset, memcpy
from libc.stdint cimport int32_t

from cymem.cymem cimport Pool
from preshed.maps cimport map_get as Map_get
from preshed.maps cimport map_set as Map_set
from preshed.maps cimport map_init as Map_init
from preshed.maps cimport MapStruct as MapC
from thinc.typedefs cimport weight_t
from thinc.api cimport Example
from thinc.api cimport ExampleC
from thinc.api cimport FeatureC


cdef class NeuralNet:
    cdef readonly Pool mem

    cdef int* widths
    cdef weight_t* weights

    cdef MapC** embed_weights
    cdef int* embed_offsets
    cdef int* embed_lengths

    cdef weight_t* gradient
    cdef weight_t** _fwd
    cdef weight_t** _bwd
    
    cdef int nr_layer
    cdef int nr_weight
    cdef int nr_feat
    cdef int nr_class
    cdef weight_t learn_rate

    cdef ExampleC allocate(self, Pool mem) except *
    cdef int set_costs(self, ExampleC* eg, int gold) except -1
    cdef int set_prediction(self, ExampleC* eg) except -1
    cdef void set_scores(self, weight_t* scores,
            const FeatureC* feats, int nr_feat) nogil

    cdef int insert_embeddings(self, const FeatureC* feats, int nr_feat) except -1
 
    cdef int update(self, ExampleC* eg) except -1

    cdef weight_t** _alloc_state(self, Pool mem) except NULL
    cdef void _clean_state(self, weight_t** state) nogil
