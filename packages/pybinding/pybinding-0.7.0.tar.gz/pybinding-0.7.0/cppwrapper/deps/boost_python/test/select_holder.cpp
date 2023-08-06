// Copyright David Abrahams 2002.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
#include <boost/python/object/class_metadata.hpp>
#include <boost/python/has_back_reference.hpp>
#include <boost/python/detail/not_specified.hpp>
#include <boost/static_assert.hpp>
#include <boost/type_traits/same_traits.hpp>
#include <boost/function/function0.hpp>
#include <boost/mpl/bool.hpp>
#include <memory>

struct BR {};

struct Base {};
struct Derived : Base {};

namespace boost { namespace python
{
  // specialization
  template <>
  struct has_back_reference<BR>
    : mpl::true_
  {
  };
}} // namespace boost::python

template <class T, class U>
void assert_same()
{
    BOOST_STATIC_ASSERT((boost::is_same<T,U>::value));
    
}

template<class Holder, class T, class... Args>
void assert_holder(){
    using namespace boost::python::objects;
    
    using h = typename class_metadata<T, Args...>::holder;
    assert_same<Holder, h>();
}

int test_main(int, char * [])
{
    using namespace boost::python::detail;
    using namespace boost::python::objects;

    assert_holder<
    	value_holder<Base>, 
    	Base
    >();

    assert_holder<
    	value_holder<BR, BR, true>,
    	BR
    >();
    assert_holder<
    	value_holder<Base, Base, true>, 
    	Base, Base
    >();
    assert_holder<
    	value_holder<BR, BR, true>, 
    	BR, BR
    >();

    assert_holder<
    	value_holder<Base, Derived, true>,
    	Base, Derived
    >();

    assert_holder<
    	pointer_holder<std::auto_ptr<Base>, Base>, 
    	Base, std::auto_ptr<Base>
    >();
    
    assert_holder<
    	pointer_holder<std::auto_ptr<Derived>, Derived, Base, true>,
    	Base, std::auto_ptr<Derived>
    >();

    assert_holder<
    	pointer_holder<std::auto_ptr<BR>, BR, BR, true>,
    	BR, std::auto_ptr<BR>
    >();

    return 0;
}

