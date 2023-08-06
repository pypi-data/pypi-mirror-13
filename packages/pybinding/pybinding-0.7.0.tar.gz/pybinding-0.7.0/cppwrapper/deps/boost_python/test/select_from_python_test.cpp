// Copyright David Abrahams 2004. Distributed under the Boost
// Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#include <boost/python/converter/arg_from_python.hpp>
#include <boost/python/type_id.hpp>
#include <iostream>
using namespace boost::python::converter;
using namespace boost;

int result;

template<class T1, class T2>
inline void assert_same() {
    if (!std::is_same<T1, T2>::value) {
         std::cout << "*********************\n";
         std::cout << python::type_id<T1>() << " != " << python::type_id<T2>() << "\n";
         std::cout << "*********************\n";
         result = 1;
   }
}

int main()
{
    assert_same<
        select_arg_from_python_t<int>,
        rvalue_from_python<int>
    >();
    
    assert_same<
        select_arg_from_python_t<int const>,
        rvalue_from_python<int const>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile>,
        rvalue_from_python<int volatile>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile>,
        rvalue_from_python<int const volatile>
    >();



    assert_same<
        select_arg_from_python_t<int*>,
        lvalue_from_python<int*>
    >();
    
    assert_same<
        select_arg_from_python_t<int const*>,
        lvalue_from_python<int const*>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile*>,
        lvalue_from_python<int volatile*>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile*>,
        lvalue_from_python<int const volatile*>
    >();




    assert_same<
        select_arg_from_python_t<int&>,
        lvalue_from_python<int&>
    >();
    
    assert_same<
        select_arg_from_python_t<int const&>,
        rvalue_from_python<int const&>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile&>,
        lvalue_from_python<int volatile&>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile&>,
        lvalue_from_python<int const volatile&>
    >();



    assert_same<
        select_arg_from_python_t<int*&>,
        lvalue_from_python<int*&>
    >();
    
    assert_same<
        select_arg_from_python_t<int const*&>,
        lvalue_from_python<int const*&>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile*&>,
        lvalue_from_python<int volatile*&>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile*&>,
        lvalue_from_python<int const volatile*&>
    >();



    assert_same<
        select_arg_from_python_t<int* const&>,
        lvalue_from_python<int*>
    >();
    
    assert_same<
        select_arg_from_python_t<int const* const&>,
        lvalue_from_python<int const*>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile* const&>,
        lvalue_from_python<int volatile*>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile* const&>,
        lvalue_from_python<int const volatile*>
    >();



    assert_same<
        select_arg_from_python_t<int*volatile&>,
        lvalue_from_python<int*volatile&>
    >();
    
    assert_same<
        select_arg_from_python_t<int const*volatile&>,
        lvalue_from_python<int const*volatile&>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile*volatile&>,
        lvalue_from_python<int volatile*volatile&>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile*volatile&>,
        lvalue_from_python<int const volatile*volatile&>
    >();



    assert_same<
        select_arg_from_python_t<int*const volatile&>,
        lvalue_from_python<int*const volatile&>
    >();
    
    assert_same<
        select_arg_from_python_t<int const*const volatile&>,
        lvalue_from_python<int const*const volatile&>
    >();
    
    assert_same<
        select_arg_from_python_t<int volatile*const volatile&>,
        lvalue_from_python<int volatile*const volatile&>
    >();

    assert_same<
        select_arg_from_python_t<int const volatile*const volatile&>,
        lvalue_from_python<int const volatile*const volatile&>
    >();
    
    return result;
}
