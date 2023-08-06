// Copyright David Abrahams 2002.
// Distributed under the Boost Software License, Version 1.0. (See
// accompanying file LICENSE_1_0.txt or copy at
// http://www.boost.org/LICENSE_1_0.txt)
#include <boost/python/bases.hpp>
#include <boost/python/detail/type_list_utils.hpp>
#include <boost/python/detail/is_xxx.hpp>
#include <type_traits>
using namespace boost::python;
namespace tl = boost::python::detail::tl;

struct A;
struct B;

template<class T>
using is_bases = detail::is_<bases, T>;

template<class... Ts>
using choose_bases_t = tl::find_if_t<tl::type_list<Ts...>, is_bases, bases<>>;

int main()
{
    static_assert(is_bases<bases<A, B>>::value, "");
    static_assert(!is_bases<bases<A, B>&>::value, "");
    static_assert(!is_bases<void*>::value, "");
    static_assert(!is_bases<int>::value, "");
    static_assert(!is_bases<int[5]>::value, "");

    using collected1 = choose_bases_t<int, char*>;
    static_assert(std::is_same<collected1, bases<>>::value, "");

    static_assert(std::is_same<choose_bases_t<int, char*, long>, bases<>>::value, "");
    
    using collected2 = choose_bases_t<int, bases<A, B>, A>;
    static_assert(std::is_same<collected2, bases<A, B>>::value, "");

    static_assert(std::is_same<choose_bases_t<int, bases<A, B>,long>, bases<A, B>>::value, "");
}
