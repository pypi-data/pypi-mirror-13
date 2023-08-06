include(PythonTesting)

bp_add_exe_test(exec STATIC CPP_SOURCES exec.cpp PY_SOURCES exec.py)
bp_add_exe_test(exec-dynamic SHARED CPP_SOURCES exec.cpp PY_SOURCES exec.py)

bp_add_py_test(crossmod_exception CPP_SOURCES crossmod_exception_a.cpp crossmod_exception_b.cpp)

bp_add_py_test(def_lambda)
bp_add_py_test(move_semantics)
bp_add_py_test(std_containers)

bp_add_py_test(injected)
bp_add_py_test(properties)
bp_add_py_test(return_arg)
bp_add_py_test(staticmethod)
bp_add_py_test(shared_ptr)
bp_add_py_test(enable_shared_from_this)
bp_add_py_test(andreas_beyer)
bp_add_py_test(wrapper_held_type)

bp_add_py_test(polymorphism2_auto_ptr PY_SOURCES polymorphism2.py)
bp_add_py_test(polymorphism)
bp_add_py_test(polymorphism2)

bp_add_py_test(auto_ptr)

bp_add_py_test(minimal)
bp_add_py_test(args)
bp_add_py_test(raw_ctor)
bp_add_py_test(numpy PY_SOURCES printer.py numeric_tests.py numarray_tests.py)
bp_add_py_test(enum)
bp_add_py_test(exception_translator)
bp_add_py_test(pearu1 PY_RUN test_cltree.py CPP_SOURCES cltree.cpp)
bp_add_py_test(try PY_RUN newtest.py CPP_SOURCES m1.cpp m2.cpp)
bp_add_py_test(const_argument)
bp_add_py_test(keywords_ PY_RUN keywords_test.py CPP_SOURCES keywords.cpp)

boost_python_add_module(builtin_converters_ext test_builtin_converters.cpp)
bp_add_py_test(builtin_converters PY_RUN test_builtin_converters.py DEPENDS builtin_converters_ext)

bp_add_py_test(test_pointer_adoption)
bp_add_py_test(operators)
bp_add_py_test(operators_wrapper)
bp_add_py_test(callbacks)
bp_add_py_test(defaults)

bp_add_py_test(object)
bp_add_py_test(class)
bp_add_py_test(list)
bp_add_py_test(long)
bp_add_py_test(dict)
bp_add_py_test(tuple)
bp_add_py_test(str)
bp_add_py_test(slice)

bp_add_py_test(virtual_functions)
bp_add_py_test(back_reference)
bp_add_py_test(implicit)
bp_add_py_test(data_members)

bp_add_py_test(ben_scott1)

bp_add_py_test(bienstman1)
bp_add_py_test(bienstman2)
bp_add_py_test(bienstman3)

bp_add_py_test(multi_arg_constructor)

bp_add_py_test(iterator_ PY_RUN iterator.py CPP_SOURCES iterator.cpp input_iterator.cpp)
bp_add_py_test(stl_iterator)

bp_add_py_test(extract)

bp_add_py_test(crossmod_opaque CPP_SOURCES crossmod_opaque_a.cpp crossmod_opaque_b.cpp)
bp_add_py_test(opaque)
bp_add_py_test(voidptr)

bp_add_py_test(pickle1)
bp_add_py_test(pickle2)
bp_add_py_test(pickle3)
bp_add_py_test(pickle4)

bp_add_py_test(nested)

bp_add_py_test(docstring)
bp_add_py_test(pytype_function)

bp_add_py_test(vector_indexing_suite)

bp_add_py_test(pointer_vector)

boost_python_add_module(map_indexing_suite_ext
                        map_indexing_suite.cpp int_map_indexing_suite.cpp a_map_indexing_suite.cpp)
bp_add_py_test(map_indexing_suite PY_RUN map_indexing_suite.py DEPENDS map_indexing_suite_ext)

bp_add_exe_test(import_ SHARED CPP_SOURCES import_.cpp PY_SOURCES import_.py)

if(WIN32)
    bp_add_py_test(calling_conventions)
    bp_add_py_test(calling_conventions_mf)
endif()

# --- unit tests of library components ---

bp_add_exe_test(destroy_test SHARED)

bp_add_exe_test(bases SHARED SUPPRESS_REGISTRY)
bp_add_exe_test(pointee SHARED SUPPRESS_REGISTRY)

bp_add_compile_test(string_literal)
bp_add_compile_test(borrowed)
bp_add_compile_test(object_manager)
bp_add_compile_test(copy_ctor_mutates_rhs)

bp_add_exe_test(upcast SHARED SUPPRESS_REGISTRY)

bp_add_compile_test(select_holder)

bp_add_exe_test(select_from_python_test STATIC SUPPRESS_REGISTRY)

bp_add_compile_test(select_arg_to_python_test)

bp_add_compile_test(raw_pyobject_fail1 WILL_FAIL)
bp_add_compile_test(raw_pyobject_fail2 WILL_FAIL)
bp_add_compile_test(as_to_python_function WILL_FAIL)
bp_add_compile_test(object_fail1 WILL_FAIL)
