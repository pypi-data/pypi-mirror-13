#ifndef BLOCK_DIAG_ILU_GOB3CSYR2HBHUEX4HJGA3584
#define BLOCK_DIAG_ILU_GOB3CSYR2HBHUEX4HJGA3584
#include <algorithm> // std::max
#include <type_traits>
#include <utility>
#include <memory>
#include <cmath> // std::abs for float and double
#include <cstdlib> // std::abs for int (must include!!)
#include <cstring> // memcpy

#ifndef NDEBUG
#include <vector>
#endif

// block_diag_ilu
// ==============
// Algorithm: Incomplete LU factorization of block diagonal matrices with weak sub-/super-diagonals
// Language: C++11
// License: Open Source, see LICENSE.txt (BSD 2-Clause license)
// Author: Björn Dahlgren 2015
// URL: https://github.com/chemreac/block_diag_ilu


namespace block_diag_ilu {

    // make_unique<T[]>() only in C++14, work around:
    // begin copy paste from http://stackoverflow.com/a/10150181/790973
    template <class T, class ...Args>
    typename std::enable_if
    <
        !std::is_array<T>::value,
        std::unique_ptr<T>
        >::type
    make_unique(Args&& ...args)
    {
        return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
    }

    template <class T>
    typename std::enable_if
    <
        std::is_array<T>::value,
        std::unique_ptr<T>
        >::type
    make_unique(std::size_t n)
    {
        typedef typename std::remove_extent<T>::type RT;
        return std::unique_ptr<T>(new RT[n]);
    }
    // end copy paste from http://stackoverflow.com/a/10150181/790973

    // Let's define an alias template for a buffer type which may
    // use (conditional compilation) either std::unique_ptr or std::vector
    // as underlying data structure.

#ifdef NDEBUG
    template<typename T> using buffer_t = std::unique_ptr<T[]>;
    template<typename T> using buffer_ptr_t = T*;
    // For use in C++14:
    // template<typename T> constexpr auto buffer_factory = make_unique<T>;
    // Work around in C++11:
    template<typename T> inline constexpr buffer_t<T> buffer_factory(std::size_t n) {
        return make_unique<T[]>(n);
    }
    template<typename T> inline constexpr T* buffer_get_raw_ptr(buffer_t<T>& buf) {
        return buf.get();
    }
#else
    template<typename T> using buffer_t = std::vector<T>;
    template<typename T> using buffer_ptr_t = T*;
    template<typename T> inline constexpr buffer_t<T> buffer_factory(std::size_t n) {
        return buffer_t<T>(n);
    }
    template<typename T> inline constexpr T* buffer_get_raw_ptr(buffer_t<T>& buf) {
        return &buf[0];
    }
#endif

#if defined(WITH_BLOCK_DIAG_ILU_DGETRF)
    inline int dgetrf_square(const int dim, double * const __restrict__ a,
                             const int lda, int * const __restrict__ ipiv) noexcept;
#else
    extern "C" void dgetrf_(const int* dim1, const int* dim2, double* a, int* lda, int* ipiv, int* info);
#endif

    extern "C" void dgbtrf_(const int *nrows, const int* ncols, const int* nsub,
                            const int *nsup, double *ab, const int *ldab, int *ipiv, int *info);

    extern "C" void dgbtrs_(const char *trans, const int *dim, const int* nsub,
                            const int *nsup, const int *nrhs, double *ab,
                            const int *ldab, const int *ipiv, double *b, const int *ldb, int *info);

    template <typename Real_t = double>
    class ColMajBlockDiagView {
    public:

        // int will suffice, decomposition scales as N**3,
        // even iterative methods (N**2) would need months
        // at 1 TFLOPS (assuming int is int32)

        Real_t *block_data, *sub_data, *sup_data;
        const std::size_t nblocks;
        const int blockw, ndiag, ld_blocks;
        const std::size_t block_stride;
        const int ld_diag;
        const std::size_t block_data_len, diag_data_len, nouter, dim;
        // ld_block for cache alignment and avoiding false sharing
        // block_stride for avoiding false sharing
        ColMajBlockDiagView(Real_t * const block_data_, Real_t * const sub_data_,
                            Real_t * const sup_data_, const std::size_t nblocks_,
                            const int blockw_, const int ndiag_,
                            const int ld_blocks_=0, const std::size_t block_stride_=0,
                            const int ld_diag_=0) :
            block_data(block_data_), sub_data(sub_data_), sup_data(sup_data_),
            nblocks(nblocks_), blockw(blockw_), ndiag(ndiag_),
            ld_blocks((ld_blocks_ == 0) ? blockw_ : ld_blocks_),
            block_stride((block_stride_ == 0) ? ld_blocks*blockw : block_stride_),
            ld_diag((ld_diag_ == 0) ? ld_blocks : ld_diag_),
            block_data_len(nblocks*block_stride),
            diag_data_len(ld_diag*(nblocks*ndiag - (ndiag*ndiag + ndiag)/2)),
            nouter((ndiag == 0) ? blockw-1 : blockw*ndiag),
            dim(blockw*nblocks) {}
        inline void set_data_pointers(buffer_ptr_t<Real_t> block_data_,
                                      buffer_ptr_t<Real_t> sub_data_,
                                      buffer_ptr_t<Real_t> sup_data_) noexcept {
            this->block_data = block_data_;
            this->sub_data = sub_data_;
            this->sup_data = sup_data_;
        }
        void dot_vec(const Real_t * const vec, Real_t * const out){
            // out need not be zeroed out before call
            const auto nblk = this->nblocks;
            const auto blkw = this->blockw;
            for (std::size_t i=0; i<nblk*blkw; ++i)
                out[i] = 0.0;
            for (std::size_t bri=0; bri<nblk; ++bri)
                for (int lci=0; lci<blkw; ++lci)
                    for (int lri=0; lri<blkw; ++lri)
                        out[bri*blkw + lri] += vec[bri*blkw + lci]*\
                            (this->block(bri, lri, lci));
            for (int di=0; di<this->ndiag; ++di)
                for (std::size_t bi=0; bi<nblk-di-1; ++bi)
                    for (int ci=0; ci<blkw; ++ci){
                        out[bi*blkw + ci] += this->sup(di, bi, ci)*vec[(bi+di+1)*blkw+ci];
                        out[(bi+di+1)*blkw + ci] += this->sub(di, bi, ci)*vec[bi*blkw+ci];
                    }
    }

    private:
        inline std::size_t diag_idx(const int diagi, const std::size_t blocki,
                                    const int coli) const noexcept {
            const std::size_t n_diag_blocks_skip = this->nblocks*diagi - (diagi*diagi + diagi)/2;
            return (n_diag_blocks_skip + blocki)*(this->ld_diag) + coli;
        }
    public:
        inline Real_t& block(const std::size_t blocki, const int rowi,
                             const int coli) const noexcept {
            return this->block_data[blocki*this->block_stride + coli*(this->ld_blocks) + rowi];
        }
        inline Real_t& sub(const int diagi, const std::size_t blocki,
                           const int coli) const noexcept {
            return this->sub_data[diag_idx(diagi, blocki, coli)];
        }
        inline Real_t& sup(const int diagi, const std::size_t blocki,
                           const int coli) const noexcept {
            return this->sup_data[diag_idx(diagi, blocki, coli)];
        }
        inline Real_t get_global(const std::size_t rowi,
                                 const std::size_t coli) const noexcept{
            const std::size_t bri = rowi / this->blockw;
            const std::size_t bci = coli / this->blockw;
            const int lri = rowi - bri*this->blockw;
            const int lci = coli - bci*this->blockw;
            if (bri == bci)
                return this->block(bri, lri, lci);
            if (lri != lci)
                return 0.0;
            if (bri > bci){ // sub diagonal
                if ((bri - bci) > (unsigned)ndiag)
                    return 0.0;
                else
                    return this->sub(bri-bci-1, bci, lci);
            } else { // super diagonal
                if ((bci - bri) > (unsigned)ndiag)
                    return 0.0;
                else
                    return this->sup(bci-bri-1, bri, lri);
            }
        }
        inline int get_banded_ld() const noexcept {
            return 1 + 3*this->nouter; // padded for use with LAPACK's dgbtrf
        }
        inline buffer_t<Real_t> to_banded() const {
            const auto ld_result = this->get_banded_ld();
            auto result = buffer_factory<Real_t>(ld_result*this->dim);
            for (unsigned int ci = 0; ci < this->dim; ++ci){
                const int row_lower = (ci < this->nouter) ? 0 : ci - this->nouter;
                const int row_upper = (ci + this->nouter + 1 > this->dim) ? this->dim :
                    ci + this->nouter + 1;
                for (int ri=row_lower; ri<row_upper; ++ri){
                    result[ld_result*ci + 2*this->nouter + ri - ci] = this->get_global(ri, ci);
                }
            }
            return result;
        }
        void set_to_1_minus_gamma_times_view(Real_t gamma, ColMajBlockDiagView &other) {
            const auto nblocks = this->nblocks;
            const auto blockw = this->blockw;
            // Scale main blocks by -gamma
            for (std::size_t bi = 0; bi < nblocks; ++bi)
                for (int ci=0; ci < blockw; ++ci)
                    for (int ri = 0; ri < blockw; ++ri)
                        this->block(bi, ri, ci) = -gamma*other.block(bi, ri, ci);

            // Add the identiy matrix
            for (std::size_t bi = 0; bi < nblocks; ++bi)
                for (int ci = 0; ci < blockw; ++ci)
                    this->block(bi, ci, ci) += 1;

            // Scale diagonals by -gamma
            for (int di = 0; di < this->ndiag; ++di)
                for (std::size_t bi=0; bi < ((nblocks <= (unsigned)di+1) ? 0 : nblocks - di - 1); ++bi)
                    for (int ci = 0; ci < blockw; ++ci){
                        this->sub(di, bi, ci) = -gamma*other.sub(di, bi, ci);
                        this->sup(di, bi, ci) = -gamma*other.sup(di, bi, ci);
                    }
        }
        inline void zero_out_blocks() noexcept {
            for (std::size_t i=0; i<(this->block_data_len); ++i){
                this->block_data[i] = 0.0;
            }
        }
        inline void zero_out_diags() noexcept {
            for (std::size_t i=0; i<(this->diag_data_len); ++i){
                this->sub_data[i] = 0.0;
            }
            for (std::size_t i=0; i<(this->diag_data_len); ++i){
                this->sup_data[i] = 0.0;
            }
        }

    };

    class LU {
#ifdef UNIT_TEST
    public:
#endif
        const int dim, nouter, ld;
        buffer_t<double> data;
        buffer_t<int> ipiv;
    public:
        LU(const ColMajBlockDiagView<double>& view) :
            dim(view.dim),
            nouter(view.nouter),
            ld(view.get_banded_ld()),
            data(view.to_banded()),
            ipiv(buffer_factory<int>(view.dim))
        {
            int info;
            dgbtrf_(&this->dim, &this->dim, &this->nouter, &this->nouter,
                    buffer_get_raw_ptr(this->data),
                    &this->ld,
                    buffer_get_raw_ptr(this->ipiv), &info);
            if (info){
                throw std::runtime_error("DGBTRF failed.");
            }
        }
        inline void solve(const double * const b, double * const x){
            const char trans = 'N'; // no transpose
            std::memcpy(x, b, sizeof(double)*this->dim);
            int info, nrhs=1;
            dgbtrs_(&trans, &this->dim, &this->nouter, &this->nouter, &nrhs,
                    buffer_get_raw_ptr(this->data), &this->ld,
                    buffer_get_raw_ptr(this->ipiv), x, &this->dim, &info);
            if (info)
                throw std::runtime_error("DGBTRS failed.");
        };
    };

    template <typename Real_t = double>
    class ColMajBlockDiagMat {
        buffer_t<Real_t> block_data, sub_data, sup_data;
    public:
        ColMajBlockDiagView<Real_t> view;
        const bool contiguous;
        ColMajBlockDiagMat(const std::size_t nblocks_,
                           const int blockw_,
                           const int ndiag_,
                           const int ld_blocks_=0,
                           const std::size_t block_stride_=0,
                           const int ld_diag_=0,
                           const bool contiguous=true) :
            view(nullptr, nullptr, nullptr, nblocks_, blockw_,
                 ndiag_, ld_blocks_, block_stride_, ld_diag_),
            contiguous(contiguous) {
            if (contiguous){
                this->block_data = buffer_factory<Real_t>(view.block_data_len +
                                                          2*view.diag_data_len);
                auto raw_ptr = buffer_get_raw_ptr(this->block_data);
                this->view.set_data_pointers(raw_ptr,
                                             raw_ptr + view.block_data_len,
                                             raw_ptr + view.block_data_len + view.diag_data_len);
            } else {
                this->block_data = buffer_factory<Real_t>(view.block_data_len);
                this->sub_data = buffer_factory<Real_t>(view.diag_data_len);
                this->sup_data = buffer_factory<Real_t>(view.diag_data_len);
                this->view.set_data_pointers(buffer_get_raw_ptr(this->block_data),
                                             buffer_get_raw_ptr(this->sub_data),
                                             buffer_get_raw_ptr(this->sup_data));
            }
        }
        buffer_ptr_t<Real_t> get_block_data_raw_ptr() {
            return buffer_get_raw_ptr(this->block_data);
        }
        buffer_ptr_t<Real_t> get_sub_data_raw_ptr() {
            return buffer_get_raw_ptr(this->sub_data);
        }
        buffer_ptr_t<Real_t> get_sup_data_raw_ptr() {
            return buffer_get_raw_ptr(this->sup_data);
        }
    };

    inline void rowpiv2rowbycol(int n, const int * const piv, int * const rowbycol) {
        for (int i = 0; i < n; ++i){
            rowbycol[i] = i;
        }
        for (int i=0; i<n; ++i){
            int j = piv[i] - 1; // Fortran indexing starts with 1
            if (i != j){
                int tmp = rowbycol[j];
                rowbycol[j] = rowbycol[i];
                rowbycol[i] = tmp;
            }
        }
    }

    inline void rowbycol2colbyrow(int n, const int * const rowbycol, int * const colbyrow){
        for (int i=0; i<n; ++i){
            for (int j=0; j<n; ++j){
                if (rowbycol[j] == i){
                    colbyrow[i] = j;
                    break;
                }
            }
        }
    }

    constexpr int diag_store_len(int N, int n, int ndiag) {
        return n*(N*ndiag - (ndiag*ndiag + ndiag)/2);
    }

    class ILU_inplace {
    public:
        ColMajBlockDiagView<double> view;
        buffer_t<int> ipiv, rowbycol, colbyrow;
#ifdef UNIT_TEST
        std::size_t nblocks() { return this->view.nblocks; }
        int blockw() { return this->view.blockw; }
        int ndiag() { return this->view.ndiag; }
        double sub_get(const int diagi, const std::size_t blocki,
                       const int coli) { return this->view.sub(diagi, blocki, coli); }
        double sup_get(const int diagi, const std::size_t blocki,
                       const int coli) { return this->view.sup(diagi, blocki, coli); }
        int piv_get(const int idx) { return this->ipiv[idx]; }
        int rowbycol_get(const int idx) { return this->rowbycol[idx]; }
        int colbyrow_get(const int idx) { return this->colbyrow[idx]; }
#endif

        // use ld_blocks and ld_diag in view to avoid false sharing
        // in parallelized execution
        ILU_inplace(ColMajBlockDiagView<double> view) :
            view(view),
            ipiv(buffer_factory<int>(view.blockw*view.nblocks)),
            rowbycol(buffer_factory<int>(view.blockw*view.nblocks)),
            colbyrow(buffer_factory<int>(view.blockw*view.nblocks)) {
            int info_ = 0;
            const auto nblocks = this->view.nblocks;
            const auto ndiag = this->view.ndiag;
#if !defined(WITH_BLOCK_DIAG_ILU_DGETRF)
            // LAPACK take pointers to integers
            int blockw = this->view.blockw;
            int ld_blocks = this->view.ld_blocks;
#else
            auto blockw = this->view.blockw;
#pragma omp parallel for
#endif
            for (std::size_t bi=0; bi<nblocks; ++bi){
#if defined(WITH_BLOCK_DIAG_ILU_DGETRF)
                int info = dgetrf_square(
                           blockw,
                           &(this->view.block(bi, 0, 0)),
                           this->view.ld_blocks,
                           &(this->ipiv[bi*blockw]));
#else
                int info;
                dgetrf_(&blockw,
                        &blockw,
                        &(this->view.block(bi, 0, 0)),
                        &(ld_blocks),
                        &(this->ipiv[bi*blockw]),
                        &info);
#endif
                if ((info != 0) && (info_ == 0))
                    info_ = info;
                for (int ci = 0; ci < blockw; ++ci){
                    for (int di = 0; (di < ndiag) && (bi+di < (nblocks) - 1); ++di){
                        this->view.sub(di, bi, ci) /= this->view.block(bi, ci, ci);
                    }
                }
                rowpiv2rowbycol(blockw, &ipiv[bi*blockw], &rowbycol[bi*blockw]);
                rowbycol2colbyrow(blockw, &rowbycol[bi*blockw], &colbyrow[bi*blockw]);
            }
            if (info_)
                throw std::runtime_error("ILU failed!");
        }
        void solve(const double * const __restrict__ b, double * const __restrict__ x) const {
            // before calling solve: make sure that the
            // block_data and sup_data pointers are still valid.
            const auto nblocks = this->view.nblocks;
            const auto blockw = this->view.blockw;
            const auto ndiag = this->view.ndiag;
            auto y = buffer_factory<double>(nblocks*blockw);
            for (std::size_t bri = 0; bri < nblocks; ++bri){
                for (int li = 0; li < blockw; ++li){
                    double s = 0.0;
                    for (int lci = 0; lci < li; ++lci){
                        s += this->view.block(bri, li, lci)*y[bri*blockw + lci];
                    }
                    for (unsigned int di = 1; di < (unsigned)ndiag + 1; ++di){
                        if (bri >= di) {
                            int ci = this->colbyrow[bri*blockw + li];
                            s += (this->view.sub(di-1, bri-di, ci) * y[(bri-di)*blockw + ci]);
                        }
                    }
                    y[bri*blockw + li] = b[bri*blockw + this->rowbycol[bri*blockw + li]] - s;
                }
            }
            for (std::size_t bri = nblocks; bri > 0; --bri){
                for (int li = blockw; li > 0; --li){
                    double s = 0.0;
                    for (int ci = li; ci < blockw; ++ci)
                        s += this->view.block(bri-1, li-1, ci)*x[(bri-1)*blockw + ci];
                    for (int di = 1; di <= ndiag; ++di) {
                        if ((bri-1) < nblocks - di){
                            int ci = this->colbyrow[(bri-1)*blockw + li-1];
                            s += this->view.sup(di-1, bri-1, ci)*x[(bri-1+di)*blockw + ci];
                        }
                    }
                    x[(bri-1)*blockw+li-1] = (y[(bri-1)*blockw + li-1] - s)\
                        /(this->view.block(bri-1, li-1, li-1));
                }
            }
        }
    };

}

#if defined(WITH_BLOCK_DIAG_ILU_DGETRF)
// int will be enough (flops of a LU decomoposition scales as N**3, and besides this is unblocked)
inline int block_diag_ilu::dgetrf_square(const int dim, double * const __restrict__ a,
                                         const int lda, int * const __restrict__ ipiv) noexcept {
    // Unblocked algorithm for LU decomposition of square matrices
    // employing Doolittle's algorithm with rowswaps.
    //
    // ipiv indexing starts at 1 (Fortran compability)
    // performance should be acceptable when leading dimension
    // of the block fits in a L1 cache line.

    if (dim == 0) return 0;

    int info = 0;
    auto A = [&](int ri, int ci) -> double& { return a[ci*lda + ri]; };
    auto swaprows = [&](int ri1, int ri2) { // this is not cache friendly
        for (int ci=0; ci<dim; ++ci){
            double temp = A(ri1, ci);
            A(ri1, ci) = A(ri2, ci);
            A(ri2, ci) = temp;
        }
    };

    for (int i=0; i<dim-1; ++i) {
        int pivrow = i;
        double absmax = std::abs(A(i, i));
        for (int j=i; j<dim; ++j) {
            // Find pivot
            double curabs = std::abs(A(j, i));
            if (curabs > absmax){
                absmax = curabs;
                pivrow = j;
            }
        }
        if ((absmax == 0) && (info == 0))
            info = pivrow+1;
        ipiv[i] = pivrow+1;
        if (pivrow != i) {
            // Swap rows
            swaprows(i, pivrow);
        }
        // Eliminate in column
        for (int ri=i+1; ri<dim; ++ri){
            A(ri, i) = A(ri, i)/A(i, i);
        }
        // Subtract from rows
        for (int ci=i+1; ci<dim; ++ci){
            for (int ri=i+1; ri<dim; ++ri){
                A(ri, ci) -= A(ri, i)*A(i, ci);
            }
        }
    }
    ipiv[dim-1] = dim;
    return info;
}
#endif

#endif
