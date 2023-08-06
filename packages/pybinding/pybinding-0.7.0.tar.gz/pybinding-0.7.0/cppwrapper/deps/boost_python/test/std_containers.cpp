#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/class.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/list.hpp>
#include <boost/python/docstring_options.hpp>

#include <tuple>
#include <vector>
#include <string>

using namespace boost::python;

BOOST_PYTHON_MODULE(std_containers_ext) {
	docstring_options::update_format(dict{
		"doc"_kw = "{python_signature}",
	});
	docstring_options::update_python_format(dict{
		"signature"_kw = "{function_name}({parameters}) -> {pytype_return}:",
		"parameter"_kw = "{name}: {pytype}{default_value}",
		"unnamed"_kw = "a{}"
	});

	// TUPLE
    def("tuple_return_to_python", []{
		return std::make_tuple(1, 2.0f, 3.0);
	});
    def("tuple_arg_to_python", [](object func) {
		func(std::make_tuple("char const*", std::string("std::string")));
	});
    def("tuple_return_from_python", [](tuple pt) {
		auto t = extract<std::tuple<int, int>>{pt}();
		return make_tuple(std::get<0>(t), std::get<1>(t));
	});
    def("tuple_arg_from_python", [](std::tuple<int, int> t) {
		return make_tuple(std::get<0>(t), std::get<1>(t));
	});
    def("tuple_empty", [](std::tuple<>) { return true; });

	// PAIR
    def("pair_return_to_python", []{
		return std::make_pair(1, 2.0f);
	});
    def("pair_arg_to_python", [](object func) {
		func(std::make_pair("char const*", std::string("std::string")));
	});
    def("pair_return_from_python", [](tuple pt) {
		auto t = extract<std::pair<int, int>>{pt}();
		return make_tuple(std::get<0>(t), std::get<1>(t));
	});
    def("pair_arg_from_python", [](std::pair<int, int> t) {
		return make_tuple(std::get<0>(t), std::get<1>(t));
	});

    // VECTOR
    def("vector_return_to_python", []{
		return std::vector<int>{1, 2, 3};
	});
    def("vector_arg_to_python", [](object func) {
		func(std::vector<std::string>{"a", "b", "c"});
	});
    def("vector_return_from_python", [](list pl) {
		return extract<std::vector<int>>{pl}();
	});
    def("vector_arg_from_python", [](std::vector<float> v) {
		return v;
	});
    def("vector_empty", [](std::vector<int>) { return true; });
}
