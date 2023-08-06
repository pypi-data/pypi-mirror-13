#include "ksdata_event.h"
#include "ksevent_engine.h"

using namespace std;
using namespace GS::EventEngine;

static PyMemberDef KSEventEngine_DataMembers[] = 
{
	{NULL, NULL, NULL, 0, NULL}
};

static PyMethodDef KSEventEngine_MethodMembers[] =      //类的所有成员函数结构列表.
{
	{"run", (PyCFunction)KSEventEngine::run, METH_NOARGS, "run event engine"},
	{"getNextEvent", (PyCFunction)KSEventEngine::getNextEvent, METH_NOARGS, "getNextEvent"},
	{"addSource", (PyCFunction)KSEventEngine::addSource, METH_VARARGS, "addSource"},
	{NULL, NULL, NULL, NULL}
};

static PyTypeObject KSEventEngineType = {
    KS_PyVarObject_HEAD_INIT(NULL, 0)
    "keystone.KSEventEngine",             /*tp_name*/
    sizeof(KSEventEngine),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)KSEventEngine::deleteMethod, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "KSEventEngine objects",           /* tp_doc */
    0,                         /* tp_traverse */
    0,                         /* tp_clear */   
	0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    KSEventEngine_MethodMembers,             /* tp_methods */
    KSEventEngine_DataMembers,             /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
	(initproc)KSEventEngine::initMethod,      				   /* tp_init */
    0,                         /* tp_alloc */
    KSEventEngine::newMethod,                 /* tp_new */
};

static PyMethodDef module_methods[] = {
    {NULL}  /* Sentinel */
};

MOD_INIT(engine)
{
	PyDateTime_IMPORT;
    PyObject* m;

    if (PyType_Ready(&KSEventEngineType) < 0)
        return MOD_ERROR_VAL;

    if (PyType_Ready(&KSDataEventType) < 0)
        return MOD_ERROR_VAL;

    // m = Py_InitModule3("engine", module_methods,
    //                    "keystone.engine.KSEventEngine.");
    MOD_DEF(m, "engine", "keystone.engine.KSEventEngine.", module_methods);

    if (m == NULL)
      return MOD_ERROR_VAL; 
    Py_INCREF(&KSEventEngineType);
    //Py_INCREF(&KSDataEventType);
    PyModule_AddObject(m, "KSEventEngine", (PyObject *)&KSEventEngineType);
    //PyModule_AddObject(m, "KSDataEvent", (PyObject *)&KSDataEventType);
    return MOD_SUCCESS_VAL(m);
}
