#!/bin/sh

V8EVAL_ROOT=`cd $(dirname $0) && pwd`

if [ `uname` = "Linux" ] ; then
  export CC=$V8EVAL_ROOT/v8/third_party/llvm-build/Release+Asserts/bin/clang
  export CXX=$V8EVAL_ROOT/v8/third_party/llvm-build/Release+Asserts/bin/clang++
fi

if [ `uname` = "Darwin" ]; then
  export CC=`which clang`
  export CXX=`which clang++`
  export CPP="`which clang` -E"
  export LINK="`which clang++`"
  export CC_host=`which clang`
  export CXX_host=`which clang++`
  export CPP_host="`which clang` -E"
  export LINK_host=`which clang++`
  export GYP_DEFINES="clang=1 mac_deployment_target=10.10"
fi

install_depot_tools() {
  export PATH=$V8EVAL_ROOT/depot_tools:$PATH
  if [ -d $V8EVAL_ROOT/depot_tools ]; then
    return 0
  fi

  cd $V8EVAL_ROOT
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
}

install_googletest() {
  if [ -d $V8EVAL_ROOT/test/googletest ]; then
    return 0
  fi

  cd $V8EVAL_ROOT/test
  git clone https://github.com/google/googletest.git
  git checkout release-1.7.0
}

install_v8() {
  if [ -d $V8EVAL_ROOT/v8 ]; then
    return 0
  fi

  cd $V8EVAL_ROOT
  fetch v8
  cd v8
  git checkout 4.9.135
  CFLAGS="-fPIC" CXXFLAGS="-fPIC" make x64.release V=1
}

install_libuv() {
  if [ -d $V8EVAL_ROOT/uv ]; then
    return 0
  fi

  cd $V8EVAL_ROOT
  git clone https://github.com/libuv/libuv.git uv
  cd uv
  git checkout v1.7.5
  sh autogen.sh
  ./configure --with-pic --disable-shared
  make V=1
}

build() {
  install_depot_tools
  install_v8
  install_libuv

  cd $V8EVAL_ROOT
  mkdir -p build
  cd build
  cmake -DCMAKE_BUILD_TYPE=Release -DV8EVAL_TEST=OFF ..
  make VERBOSE=1
}

build_go() {
  $V8EVAL_ROOT/go/build.sh
}

build_python() {
  $V8EVAL_ROOT/python/build.sh
}

build_ruby() {
  $V8EVAL_ROOT/ruby/build.sh
}

docs() {
  cd $V8EVAL_ROOT/docs
  rm -rf ./html
  doxygen

  $V8EVAL_ROOT/python/build.sh docs
}

test() {
  build
  install_googletest

  cd $V8EVAL_ROOT/build
  cmake -DCMAKE_BUILD_TYPE=Release -DV8EVAL_TEST=ON ..
  make VERBOSE=1
  ./test/v8eval-test || exit 1

  cd ..
  ./go/build.sh test || exit 1
  ./python/build.sh test || exit 1
  ./ruby/build.sh test || exit 1
}

# dispatch subcommand
SUBCOMMAND="$1";
case "${SUBCOMMAND}" in
  ""       ) build ;;
  "go"     ) build_go ;;
  "python" ) build_python ;;
  "ruby"   ) build_ruby ;;
  "docs"   ) docs ;;
  "test"   ) test ;;
  *        ) echo "unknown subcommand: ${SUBCOMMAND}"; exit 1 ;;
esac
