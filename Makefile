TIMEOUT = $(shell command -v timeout 2> /dev/null)
OVO_TIMEOUT ?= 10s
ifdef TIMEOUT
	TIMEOUT = timeout -k 5s $(OVO_TIMEOUT)
endif

# From MKL linkline advisor
# https://software.intel.com/content/www/us/en/develop/tools/oneapi/components/onemkl/link-line-advisor.html
ifeq (${ILP64},1)
	CXXFLAGS=-fiopenmp -fopenmp-targets=spir64 -DMKL_ILP64 -I${MKLROOT}/include
	MATH_LIB_FLAGS=-fsycl  -L${MKLROOT}/lib/intel64 -lmkl_sycl -lmkl_intel_ilp64 -lmkl_intel_thread -lmkl_core -liomp5 -lsycl -lOpenCL -lstdc++ -lpthread -lm -ldl
else
	CXXFLAGS=-fiopenmp -fopenmp-targets=spir64 -I${MKLROOT}/include
	MATH_LIB_FLAGS=-fsycl  -L${MKLROOT}/lib/intel64 -lmkl_sycl -lmkl_intel_lp64 -lmkl_intel_thread -lmkl_core -liomp5 -lsycl -lOpenCL -lstdc++ -lpthread -lm -ldl
endif

SRC = $(wildcard *.cpp)
.PHONY: exe
exe: $(SRC:%.cpp=%.exe)

pEXE = $(wildcard *.exe)
.PHONY: run
run: $(addprefix run_, $(basename $(pEXE)))

%.exe: %.cpp
	-$(CXX) $(CXXFLAGS) $(MATH_LIB_FLAGS) $< -o $@


run_%: %.exe
	-$(TIMEOUT) ./$<

.PHONY: clean
clean:
	rm -f -- $(pEXE) 
