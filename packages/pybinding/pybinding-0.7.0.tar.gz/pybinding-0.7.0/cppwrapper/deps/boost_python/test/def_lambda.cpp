#include <boost/python/module.hpp>
#include <boost/python/def.hpp>
#include <boost/python/class.hpp>
#include <boost/python/tuple.hpp>
#include <boost/python/docstring_options.hpp>

#include <string>

using namespace boost::python;

struct X {
	int value = 10;
};

BOOST_PYTHON_MODULE(def_lambda_ext) {
	docstring_options::update_format(dict{
		"doc"_kw = "{python_signature}",
	});
	docstring_options::update_python_format(dict{
		"signature"_kw = "{function_name}({parameters}) -> {pytype_return}:",
		"parameter"_kw = "{name}: {pytype}{default_value}",
	});

	def("captureless", []{
		return "Hello World";
	});

	auto a = 1;
	def("capture_const", [a]{
		return a;
	});

	def("capture_mutable", [a]() mutable {
		return ++a;
	});

	def("with_params", [](std::string s, int i) {
		return s + std::to_string(i);
	}, args("s", "i"));

	def("and_defaults", [](object o, std::string s, int i, bool b) {
		return boost::python::make_tuple(o, s, i, b);
	}, args("o", "s", "i"_kw=7, "b"_kw=false));


	class_<X>{"X"}
	.def_readonly("value", &X::value)
	.def("static_method", []{
		return "static";
	})
	.staticmethod("static_method")
	.def("method", [](X const& x, int i) {
		return x.value + i;
	})
	.def("add", [](X& x, int i) {
		x.value += i;
	}, args("self", "value"))
	;
}
