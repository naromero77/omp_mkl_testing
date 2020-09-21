#include <iostream>
#include "mkl.h"
#include "mkl_omp_offload.h"

#define SIZE 1024


bool almost_equal(double x, double gold, double tol) {
  return gold * (1-tol) <= x && x <= gold * (1 + tol);
}


int main( int argc, char* argv[] )
{

  double *x = (double *)malloc( sizeof(double)*SIZE);

  double *y = (double *)malloc( sizeof(double)*SIZE);


  double *z_cpu = (double *)malloc( sizeof(double)*SIZE);
  double *z_gpu = (double *)malloc( sizeof(double)*SIZE);




  const int incx = 1;
  const int incy = 1;

  for(int i=0;i<SIZE;i++)
    {

      x[i] = 1;

      y[i] = 1;


      z_gpu[i] = 1;
      z_gpu[i] = 1;

    }


   cblas_ddot(SIZE, x, incx, y, incx);


#pragma omp target data map(to:x_input[0:SIZE],y[0:SIZE])
    {
      #pragma omp target variant dispatch use_device_ptr(x, y) 

      cblas_ddot(SIZE, x, incx, y, incx);

    }



  for(int i=0;i<SIZE;i++)
    {

  if (!almost_equal(z_gpu[i], z_cpu[i], 0.1)) {
    std::cerr << "Expected: " << z_cpu[i] << " Got: " << z_gpu[i] << std::endl;
    std::exit(112);
  }

    }


  return 0;
}