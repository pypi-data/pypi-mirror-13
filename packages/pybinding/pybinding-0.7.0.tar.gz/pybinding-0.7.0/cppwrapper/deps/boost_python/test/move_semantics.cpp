// Copyright David Abrahams 2002.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)

#include <boost/python/module.hpp>
#include <boost/python/class.hpp>
#include <boost/python/extract.hpp>
#include <boost/python/def.hpp>
#include <boost/python/implicit.hpp>
#include <boost/python/tuple.hpp>
#include "test_class.hpp"

#include <memory>

using namespace boost::python;

struct movable {
    movable() = default;
    movable(movable const&) : copied{true} {}
    movable(movable&&) : moved{true} {}

    bool copied = false;
    bool moved = false;
};

struct copyonly {
    copyonly() = default;
    copyonly(copyonly const&) : copied{true} {}

    bool copied = false;
    bool moved = false;
};

struct moveonly {
    moveonly() = default;
    moveonly(moveonly&&) : moved{true} {}

    bool copied = false;
    bool moved = false;
};

template<class T>
struct rvalue_converter {
    rvalue_converter() {
        converter::registry::push_back(&convertible, &construct, type_id<T>());
    }
    
    static void* convertible(PyObject* source) { return source; }

    static void construct(PyObject* /*source*/, converter::rvalue_from_python_stage1_data* data) {
        void* storage = ((converter::rvalue_from_python_storage<T>*)data)->storage.bytes;
        new (storage) T{};
        data->convertible = storage;
    }
};

template<class T>
tuple rvalue(T m) { return make_tuple(m.copied, m.moved); }
template<class T>
tuple rvalue_const_ref(T const& m) { return make_tuple(m.copied, m.moved); }

// ================================================================================================

using X = test_class<>;
struct Y : X {
    Y(int n) : X(n) {};
};

int look(std::unique_ptr<X> const& x) {
    return (x.get()) ? x->value() : -1;
}

int steal(std::unique_ptr<X> x) {
    return x->value();
}

int maybe_steal(std::unique_ptr<X>& x, bool doit) {
    int n = x->value();
    if (doit)
        x.release();
    return n;
}

std::unique_ptr<X> make() {
    return std::unique_ptr<X>(new X(77));
}

std::unique_ptr<X> callback(object f) {
    std::unique_ptr<X> x(new X(77));
    return call<std::unique_ptr<X> >(f.ptr(), x);
}

std::unique_ptr<X> extract_(object o) {
    return extract<std::unique_ptr<X>>(o)();
}


BOOST_PYTHON_MODULE(move_semantics_ext) {
    rvalue_converter<movable>{};
    rvalue_converter<copyonly>{};
    rvalue_converter<moveonly>{};
    def("movable_rvalue", rvalue<movable>);
    def("movable_rvalue_const_ref", rvalue_const_ref<movable>);
    def("copyonly_rvalue", rvalue<copyonly>);
    def("copyonly_rvalue_const_ref", rvalue_const_ref<copyonly>);
    def("moveonly_rvalue", rvalue<moveonly>);
    def("moveonly_rvalue_const_ref", rvalue_const_ref<moveonly>);

    class_<X, std::unique_ptr<X>, noncopyable>("X", init<int>())
        .def("value", &X::value)
    ;
    class_<Y, std::unique_ptr<Y>, bases<X>, noncopyable>("Y", init<int>());
    implicitly_convertible<std::unique_ptr<Y>, std::unique_ptr<X> >();
    
    def("look", look);
    def("steal", steal);
    def("maybe_steal", maybe_steal);
    def("make", make);
    def("callback", callback);
    def("extract", extract_);
}

#include "module_tail.cpp"

