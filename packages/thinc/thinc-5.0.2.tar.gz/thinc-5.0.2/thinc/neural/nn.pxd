# cython: profile=True
# cython: cdivision=True
#from __future__ import print_function
#cimport cython
#from libc.string cimport memset, memcpy
#from libc.math cimport sqrt as c_sqrt
#from libc.stdint cimport int32_t
#import numpy
#import numpy.random
#
#from cymem.cymem cimport Pool
#
#from preshed.maps cimport map_init as Map_init
#from preshed.maps cimport map_get as Map_get
#from preshed.maps cimport map_set as Map_set
#
#from .structs cimport NeuralNetC, OptimizerC, FeatureC, BatchC, ExampleC, EmbeddingC, MapC
#from .structs cimport IteratorC
#from .typedefs cimport weight_t
#from .blas cimport Vec, MatMat, MatVec, VecVec
#from .eg cimport Batch, Example
#
#
#cdef extern from "math.h" nogil:
#    float expf(float x)
#    float sqrtf(float x)
#
#
#DEF EPS = 0.000001 
#DEF ALPHA = 1.0
# The input/output of the fwd/bwd pass can be confusing. Some notes.
#
# Forward pass. in0 is at fwd_state[0]. Activation of layer 1 is
# at fwd_state[1]
# 
# in0 = input_
# in1 = act0 = ReLu(in0 * W0 + b0)
# in2 = act1 = ReLu(in1 * W1 + b1)
# out = act2 = Softmax(in2 * W2 + b2)

# Okay so our scores are at fwd_state[3]. Our loss will live there too.
# The loss will then be used to calculate the gradient for layer 2.
# We now sweep backward, and calculate the next loss, which will be used
# to calculate the gradient for layer 1, etc.
#
# So, the total loss is at bwd_state[3]
# 
# g2 = d3 = out - target
# g1 = d2 = Back(d3, in2, w2, b2)
# g0 = d1 = Back(d2, in1, w1, b1)
# gE = d0 = Back(d1, in0, w0, b0)
# 
# gE here refers to the 'fine tuning' vector, for word embeddings
# Layers go:
# 0. in u
# 1. A1 x = Wu+b
# 2. A2 u = y = elu(BN(x))
# 3. B1 x = Wu+b
# 4. B2 u = y = elu(BN(x))
# 5. S  u = softmax(Wu)
# Pre-iter: Bwd.softmax places the top loss in 5
# Iter 0: Read from 5 write dL/dY to 4, dL/dX to 3
# Iter 1: Read from 3, write dL/dY to 2, dL/dX to 1
# Post-iter: Write dL/dX to 0 for fine-tuning


#cdef class NeuralNet:
#    cdef readonly Pool mem
#    cdef readonly Example eg
#    cdef NeuralNetC c

#    @staticmethod
#    cdef inline void predictC(ExampleC* egs,
#            int nr_eg, const NeuralNetC* nn) nogil:
#        cdef int i
#        for i in range(nr_eg):
#            eg = &egs[i]
#            if nn.embeds is not NULL and eg.features is not NULL:
#                Embedding.set_input(eg.fwd_state[0],
#                    eg.features, eg.nr_feat, nn.embeds)
#            NN.forward(eg.fwd_state, nn.fwd_norms,
#                nn.weights, nn.widths, nn.nr_layer, nn.alpha)
#            Example.set_scores(eg,
#                eg.fwd_state[(nn.nr_layer*2)-2])
#     
#    @staticmethod
#    @cython.cdivision(True)
#    cdef inline void updateC(NeuralNetC* nn, weight_t* gradient, ExampleC* egs,
#            int nr_eg) nogil:
#        if nr_eg == 0:
#            return
#        cdef int i
#        for i in range(nr_eg):
#            eg = &egs[i]
#            NN.backward(eg.bwd_state, nn.bwd_norms,
#                eg.costs, eg.fwd_state, nn.fwd_norms, nn.weights, nn.widths,
#                nn.nr_layer, nn.alpha)
#        for i in range(nr_eg):
#            NN.gradient(gradient,
#                eg.bwd_state, eg.fwd_state, nn.widths, nn.nr_layer)
#        nn.opt.update(nn.opt, nn.opt.params, nn.weights, gradient,
#            1.0, nn.nr_weight)
#        # Fine-tune the embeddings
#        # This is sort of wrong --- we're supposed to average over the minibatch.
#        # However, most words are rare --- so most words will only have non-zero
#        # gradient for 1 or 2 examples anyway.
#        if nn.embeds is not NULL:
#            for i in range(nr_eg):
#                eg = &egs[i]
#                if eg.features is not NULL:
#                    Embedding.fine_tune(nn.opt, nn.embeds, eg.fine_tune,
#                        eg.bwd_state[0], nn.widths[0], eg.features, eg.nr_feat)
# 
#    @staticmethod
#    cdef inline void insert_embeddingsC(EmbeddingC* layer, Pool mem,
#            const ExampleC* egs, int nr_eg) except *:
#        for i in range(nr_eg):
#            eg = &egs[i]
#            for j in range(eg.nr_feat):
#                feat = eg.features[j]
#                emb = <weight_t*>Map_get(layer.tables[feat.i], feat.key)
#                if emb is NULL:
#                    emb = <weight_t*>mem.alloc(layer.lengths[feat.i], sizeof(weight_t))
#                    Initializer.normal(emb,
#                        0.0, 1.0, layer.lengths[feat.i])
#                    # We initialize with the defaults here so that we only have
#                    # to insert during training --- on the forward pass, we can
#                    # set default. But if we're doing that, the back pass needs
#                    # to be dealing with the same representation.
#                    #memcpy(emb,
#                    #    layer.defaults[feat.i], sizeof(weight_t) * layer.lengths[feat.i])
#                    Map_set(mem, layer.tables[feat.i], feat.key, emb)
#
#
#cdef class NN:
#    @staticmethod
#    cdef inline int nr_weight(int nr_out, int nr_in) nogil:
#        return nr_out * nr_in + nr_out * 3
#
#    @staticmethod
#    cdef inline void forward(activation_t feed_forward, weight_t** fwd, weight_t** norms,
#                        const weight_t* weights,
#                        const int* widths, int n, weight_t alpha,
#                        activation_t activate) nogil:
#        cdef IteratorC it
#        it.i = 0
#        cdef const weight_t* residual = NULL
#        cdef int width = 0
#        while NN.iter(&it, widths, n-2, 1):
#            activate(fwd, norms,
#                it, weights, widths, n, alpha)
#        linear(fwd[it.above],
#            fwd[it.below], &weights[it.W], &weights[it.bias], it.nr_out, it.nr_in)
#        softmax(fwd[it.above],
#            it.nr_out)
#
#    @staticmethod
#    cdef inline void backward(weight_t** bwd, weight_t** bwd_norms,
#            const weight_t* costs,
#            const weight_t* const* fwd,
#            const weight_t* const* fwd_norms,
#            const weight_t* weights,
#            const int* widths,
#            int n,
#            weight_t alpha) nogil:
#        cdef IteratorC it
#        it.i = n-1
#        NN.iter(&it, widths, n, -1)
#        Bwd.softmax(bwd[it.below],
#            costs, fwd[it.below], widths[n-1])
#        while NN.iter(&it, widths, n, -1):
#            ELU.backward(bwd[it.below], bwd[it.here],
#                bwd[it.above], fwd[it.below], &weights[it.W], it.nr_out, it.nr_in)
#        # The delta at bwd_state[0] can be used to 'fine tune' e.g. word vectors
#        MatVec.T_dot(bwd[it.below],
#            &weights[it.W], bwd[it.above], it.nr_out, it.nr_in)
#   
#    @staticmethod
#    cdef inline void gradient(weight_t* gradient,
#            const weight_t* const* bwd,
#            const weight_t* const* fwd,
#            const int* widths, int n) nogil: 
#        cdef IteratorC it
#        it.i = 0
#        while NN.iter(&it, widths, n-1, 1):
#            MatMat.add_outer_i(&gradient[it.W], # Gradient of synapse weights
#                bwd[it.above], fwd[it.below], it.nr_out, it.nr_in)
#            VecVec.add_i(&gradient[it.bias], # Gradient of bias weights
#                bwd[it.above], 1.0, it.nr_out)
#            #MatMat.add_outer_i(&gradient[it.gamma], # Gradient of gammas
#            #    bwd[it.here], fwd[it.here], it.nr_out, 1)
#            #VecVec.add_i(&gradient[it.beta], # Gradient of betas
#            #    bwd[it.here], 1.0, it.nr_out)
#
#cdef inline void activate(weight_t** fwd, weight_t** for_bn,
#        const weight_t* weights, int n, weight_t alpha, IteratorC it) nogil:
#    above = fwd[it.above]
#    here = fwd[it.here]
#    below = fwd[it.below]
#    Ex = for_bn[it.Ex]
#    Vx = for_bn[it.Vx]
#    W = &weights[it.W]
#    bias = &weights[it.bias]
#    gamma = &weights[it.gamma]
#    nr_in = it.nr_in
#    nr_out = it.nr_out
#
#    update_normalizers(Ex, Vx,
#        below, n, alpha)
#    normalize(below, here,
#        Ex, Vx, gamma, beta, nr_in) 
#    linear(above,
#        below, W, bias, nr_out, nr_in)
#    ELU(above, here,
#        below, W, bias, nr_out, nr_in)
#
#
#cdef inline void backprop(weight_t** bwd, weight_t** for_bn,
#    const weight_t* weights, int n, weight_t alpha, IteratorC it) nogil:
#    d_in = bwd[it.above]
#    d_out = bwd[it.below]
#    W = &weights[it.W]
#    bias = &weights[it.bias]
#    beta = &weights[it.beta]
#    gamma = &weights[it.gamma]
#
#    MatVec.T_dot(d_out,
#        W, d_in, nr_out, nr_wide)
#    # Stash dE/dY for backprop to gamma and beta
#    memcpy(d_cache,
#        d_out, sizeof(d_cache[0]) * nr_wide)
#    # Convert dE/dY to dE/dXh in place
#    VecVec.mul_i(d_out,
#        gamma, nr_wide)
#    update_denormalizers(dEdXh, dEdXh_dot_Xh,
#        d_out, Xh, alpha, nr_wide)
#    # Convert dE/dXh to dE/dX in place
#    # i.e. backprop through the normalization
#    denormalize(d_out,
#        dEdXh, dEdXh_dot_Xh, Xh, Vx, nr_wide)
#    # Backprop the ELU transformation
#    # Does this have to be above??
#    for i in range(nr_wide):
#        if x_norm[i] < 0:
#            delta_out[i] *= signal_in[i] + ALPHA
#
#
#cdef class ELU:
#    @staticmethod
#    cdef inline void norm_forward(weight_t* out, weight_t* tmp,
#            const weight_t* in_, const weight_t* E_out, const weight_t* V_out,
#            const weight_t* W, const weight_t* bias, const weight_t* gamma,
#            int nr_out, int nr_wide, weight_t alpha) nogil:
#        cdef int i
#        MatVec.dot(out, # x = weights * input
#            W, in_, nr_out, nr_wide)
#        # Update estimates of mean and variance
#        Fwd.estimate_normalizers(E_out, V_out, 
#            out, alpha, nr_out)
#        # Normalize
#        VecVec.add_i(out,
#            E_out, -1.0, nr_out)
#        for i in range(nr_out):
#            out[i] /= sqrtf(V_out[i] + EPS)
#        memcpy(tmp,
#            out, sizeof(tmp[0]) * nr_out)
#        VecVec.mul_i(out,
#            gamma, nr_out)
#        # Bias
#        VecVec.add_i(out,
#            bias, 1.0, nr_out)
#        # Apply ELU non-linearity
#        for i in range(nr_out):
#            if out[i] < 0:
#                out[i] = ALPHA * (expf(out[i])-1)
#
#    @staticmethod
#    cdef inline void norm_backward(weight_t* d_out, weight_t* d_cache,
#                                   weight_t* norm1, weight_t* norm2,
#            const weight_t* d_in, const weight_t* x, const weight_t* xh,
#            const weight_t* gamma) nogil:
#    
#    @staticmethod
#    cdef inline void forward(weight_t* out, weight_t* tmp,
#            const weight_t* in_, const weight_t* W, const weight_t* bias,
#            int nr_out, int nr_wide) nogil:
#        MatVec.dot(out,
#            W, in_, nr_out, nr_wide)
#        # Bias
#        VecVec.add_i(out,
#            bias, 1.0, nr_out)
#        cdef int i
#        for i in range(nr_out):
#            if out[i] < 0:
#                out[i] = ALPHA * (expf(out[i])-1)
#
#    @staticmethod
#    cdef inline void backward(weight_t* delta_out, weight_t* tmp,
#                        const weight_t* delta_in,  # Len == nr_out
#                        const weight_t* signal_in, # Len == nr_wide
#                        const weight_t* W,
#                        int32_t nr_out,
#                        int32_t nr_wide) nogil:
#        MatVec.T_dot(delta_out,
#            W, delta_in, nr_out, nr_wide)
#        cdef int i
#        for i in range(nr_wide):
#            if signal_in[i] < 0:
#                delta_out[i] *= signal_in[i] + ALPHA
#    
#
#cdef class Rectifier:
#    @staticmethod
#    cdef inline void forward(weight_t* out,
#            const weight_t* in_, const weight_t* W, const weight_t* bias,
#            int nr_out, int nr_wide) nogil:
#        # We're a layer of nr_wide cells, which we can think of as features.
#        # We write to an array of nr_out activations, one for each conenction
#        # to the next layer. We can think of the cells in the next layer like classes:
#        # we want to know whether we make that cell activate.
#        # 
#        # It's tempting to think at first as though we output nr_wide activations.
#        # We *receive* nr_wide activations. What we're determining now is,
#        # given those activations, our weights and our biases, what's the
#        # state of the next layer?
#        MatVec.dot(out,
#            W, in_, nr_out, nr_wide)
#        # Bias
#        VecVec.add_i(out,
#            bias, 1.0, nr_out)
#        cdef int32_t i
#        for i in range(nr_out):
#            # Writing this way handles NaN
#            if not (out[i] > 0):
#                out[i] = 0
#
#    @staticmethod
#    cdef inline void backward(weight_t* delta_out,       # Len == nr_wide
#                        const weight_t* delta_in,  # Len == nr_out
#                        const weight_t* signal_in, # Len == nr_wide
#                        const weight_t* W,
#                        int32_t nr_out,
#                        int32_t nr_wide) nogil:
#        # delta = W.T.dot(prev_delta) * d_relu(signal_in)
#        # d_relu(signal_in) is a binary vector, 0 when signal_in < 0
#        # So, we do our dot product, and then clip to 0 on the dimensions where
#        # signal_in is 0
#        # Note that prev_delta is a column vector (the error of our output),
#        # while delta is a row vector (the error of our neurons, which must match
#        # the input layer's width)
#        MatVec.T_dot(delta_out,
#            W, delta_in, nr_out, nr_wide)
#        cdef int32_t i
#        for i in range(nr_wide):
#            if signal_in[i] < 0:
#                delta_out[i] = 0
#    
#
#cdef inline void linear(weight_t* out,
#        const weight_t* in_, const weight_t* W, const weight_t* bias,
#        int nr_out, int nr_wide) nogil:
#    MatVec.dot(out,
#        W, in_, nr_out, nr_wide)
#    VecVec.add_i(out,
#        bias, 1.0, nr_out)
#
#
#cdef inline void normalize(weight_t* x, weight_t* Ex, weight_t* Vx,
#        int n, weight_t alpha) nogil:
#    for i in range(n):
#        x[i] = (x[i] - Ex[i]) / sqrf(V_x[i] + EPS)
#
#
#cdef inline void update_normalizers(weight_t* Ex, weight_t* Vx,
#        const weight_t* x, weight_t alpha, int n) nogil:
#    # Upd EMA estimate of mean and variance
#    # See eq at the end of this:
#    # http://nfs-uxsup.csx.cam.ac.uk/~fanf2/hermes/doc/antiforgery/stats.pdf
#    cdef int i
#    cdef weight_t diff, incr
#    for i in range(n):
#        diff = x[i] - E_x[i]
#        incr = alpha * diff
#        V_x[i] = (1.0 - alpha) * (V_x[i] + diff * incr)
#        E_x[i] += incr
#
#
#cdef inline void residual(weight_t* out,
#        const weight_t* const* prev, const int* widths, int i) nogil:
#    pass
#    #if nr_in == nr_out:
#    #    VecVec.add_i(out,
#    #        in_, 1.0, nr_out)
#
#
#cdef inline void softmax(weight_t* out,
#        int nr_out) nogil:
#    #w = exp(w - max(w))
#    Vec.add_i(out,
#        -Vec.max(out, nr_out), nr_out)
#    Vec.exp_i(out,
#        nr_out)
#    #w = w / sum(w)
#    cdef weight_t norm = Vec.sum(out, nr_out)
#    if norm != 0:
#        Vec.div_i(out,
#            norm, nr_out)
#
#
#
#cdef inline void delta_log_loss(weight_t* loss,
#        const weight_t* costs, const weight_t* scores, int nr_out) nogil:
#    # This assumes only one true class
#    cdef int i
#    for i in range(nr_out):
#        loss[i] = scores[i] - (costs[i] == 0)
#
#cdef inline void normalize(weight_t* bwd,
#        const weight_t* E_dEdXh, const weight_t* E_dEdXh_dot_Xh,
#            const weight_t* Xh, const weight_t* V_x, int n) nogil:
#        # Simplification taken from Caffe, I think by cdoersch
#        # if X' = (X-mean(X))/sqrt(var(X)+eps), then
#        # dE/dX =
#        #   (dE/dX' - mean(dE/dX') - mean(dE/dX' * X') * X')
#        #     ./ sqrt(var(X) + eps)
#        # bwd is dE/dX' to start with. We change it to dE/dX in-place.
#        for i in range(n):
#            bwd[i] -= E_dEdXh[i] - E_dEdXh_dot_Xh[i] * Xh[i]
#            bwd[i] /= c_sqrt(V_x[i] + EPS)
#
#    @staticmethod
#    cdef inline void estimate_normalizers(weight_t* E_bwd, weight_t* E_bwd_dot_fwd,
#            const weight_t* bwd, const weight_t* fwd, weight_t alpha, int n) nogil:
#        # Update EMA estimate of mean(dL/dX_hat)
#        Vec.mul_i(E_bwd,
#            alpha, n)
#        VecVec.add_i(E_bwd,
#            bwd, 1-alpha, n)
#        # Update EMA estimate of mean(dE/dX_hat \cdot X_hat)
#        Vec.mul_i(E_bwd_dot_fwd,
#            alpha, n)
#        for i in range(n):
#            E_bwd_dot_fwd[i] += (1-alpha) * bwd[i] * fwd[i]
#
#
#cdef class Embedding:
#    cdef Pool mem
#    cdef EmbeddingC* c
#
#    @staticmethod
#    cdef inline void init(EmbeddingC* self, Pool mem, vector_widths, features) except *: 
#        assert max(features) < len(vector_widths)
#        # Create tables, which may be shared between different features
#        # e.g., we might have a feature for this word, and a feature for next
#        # word. These occupy different parts of the input vector, but draw
#        # from the same embedding table.
#        uniqs = <MapC*>mem.alloc(len(vector_widths), sizeof(MapC))
#        uniq_defaults = <weight_t**>mem.alloc(len(vector_widths), sizeof(void*))
#        for i, width in enumerate(vector_widths):
#            Map_init(mem, &uniqs[i], 8)
#            uniq_defaults[i] = <weight_t*>mem.alloc(width, sizeof(weight_t))
#            Initializer.normal(uniq_defaults[i],
#                0.0, 1.0, width)
#        self.offsets = <int*>mem.alloc(len(features), sizeof(int))
#        self.lengths = <int*>mem.alloc(len(features), sizeof(int))
#        self.tables = <MapC**>mem.alloc(len(features), sizeof(void*))
#        self.defaults = <weight_t**>mem.alloc(len(features), sizeof(void*))
#        offset = 0
#        for i, table_id in enumerate(features):
#            self.tables[i] = &uniqs[table_id]
#            self.lengths[i] = vector_widths[table_id]
#            self.defaults[i] = uniq_defaults[table_id]
#            self.offsets[i] = offset
#            offset += vector_widths[table_id]
#
#    @staticmethod
#    cdef inline void set_input(weight_t* out, const FeatureC* features, int nr_feat,
#            const EmbeddingC* layer) nogil:
#        for i in range(nr_feat):
#            feat = features[i]
#            emb = <weight_t*>Map_get(layer.tables[feat.i], feat.key)
#            if emb == NULL:
#                emb = layer.defaults[feat.i]
#            VecVec.add_i(&out[layer.offsets[feat.i]], 
#                emb, feat.val, layer.lengths[feat.i])
#
#    @staticmethod
#    cdef inline void fine_tune(OptimizerC* opt, EmbeddingC* layer, weight_t* fine_tune,
#                               const weight_t* delta, int nr_delta,
#                               const FeatureC* features, int nr_feat) nogil:
#        for i in range(nr_feat):
#            # Reset fine_tune, because we need to modify the gradient
#            memcpy(fine_tune, delta, sizeof(weight_t) * nr_delta)
#            feat = features[i]
#            gradient = &fine_tune[layer.offsets[feat.i]]
#            weights = <weight_t*>Map_get(layer.tables[feat.i], feat.key)
#            params = <weight_t*>Map_get(opt.embed_params.tables[feat.i], feat.key)
#            ## These should never be null.
#            if weights is not NULL and params is not NULL:
#                opt.update(opt, params, weights, gradient,
#                    feat.val, layer.lengths[feat.i])
#
#
#cdef class Initializer:
#    @staticmethod
#    cdef inline void normal(weight_t* weights, weight_t loc, weight_t scale, int n) except *:
#        # See equation 10 here:
#        # http://arxiv.org/pdf/1502.01852v1.pdf
#        values = numpy.random.normal(loc=0.0, scale=scale, size=n)
#        for i, value in enumerate(values):
#            weights[i] = value
#
#    @staticmethod
#    cdef inline void constant(weight_t* weights, weight_t value, int n) nogil:
#        for i in range(n):
#            weights[i] = value
