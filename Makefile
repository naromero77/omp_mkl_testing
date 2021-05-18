TIMEOUT = $(shell command -v timeout 2> /dev/null)
OVO_TIMEOUT ?= 10s
ifdef TIMEOUT
	TIMEOUT = timeout -k 5s $(OVO_TIMEOUT)
endif

MATH_LIB_FLAGS=-fiopenmp -fopenmp-targets=spir64  -fsycl  -L${MKLROOT}/lib/intel64 -lmkl_sycl -lmkl_intel_ilp64 -lmkl_intel_thread -lmkl_core -liomp5 -lsycl -lOpenCL -lstdc++ -lpthread -lm -ldl

SRC = $(wildcard *.cpp)
.PHONY: exe
exe: $(SRC:%.cpp=%.exe)

pEXE = $(wildcard *.exe)
.PHONY: run
run: $(addprefix run_, $(basename $(pEXE)))

CXXFLAGS = -fiopenmp -fopenmp-targets=spir64 -DMKL_ILP64 -I${MKLROOT}/include

%.exe: %.cpp
	-$(CXX) $(CXXFLAGS) $(MATH_LIB_FLAGS) $< -o $@


run_%: %.exe
	-$(TIMEOUT) ./$<

.PHONY: clean
clean:
	rm -f -- $(pEXE) 
