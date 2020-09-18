#include <iostream>
#include "mkl.h"
#include "mkl_omp_offload.h"

#define SIZE 1024


bool almost_equal(float x, float gold, float tol) {
  return gold * (1-tol) <= x && x <= gold * (1 + tol);
}


int main( int argc, char* argv[] )
{

  float *x = (float *)malloc( sizeof(float)*SIZE);

  float *y = (float *)malloc( sizeof(float)*SIZE);


  float *z_cpu = (float *)malloc( sizeof(float)*SIZE);
  float *z_gpu = (float *)malloc( sizeof(float)*SIZE);




  const int incx = 1;
  const int incy = 1;

  for(int i=0;i<SIZE;i++)
    {

      x[i] = 1;

      y[i] = 1;


      z_gpu[i] = 1;
      z_gpu[i] = 1;

    }


   cblas_sdot(SIZE, x, incx, y, incx);


#pragma omp target data map(to:x_input[0:SIZE],y[0:SIZE])
    {
      #pragma omp target variant dispatch use_device_ptr(x, y) 

      cblas_sdot(SIZE, x, incx, y, incx);

    }



  for(int i=0;i<SIZE;i++)
    {

  if (!almost_equal(z[i]_gpu, z[i]_cpu, 0.1)) {
    std::cerr << "Expected: " << z[i]_cpu << " Got: " << z[i]_gpu << std::endl;
    std::exit(112);

    }


  return 0;
}