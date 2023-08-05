#include <Python.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/io.h>

static PyObject* readport(PyObject* self, PyObject *args)
{

    /* Open registers */
    ioperm(0x378,1,1);
    ioperm(0x379,1,1);
    ioperm(0x37A,1,1);

    char *reg;

    if (!PyArg_ParseTuple(args, "s", &reg))
    {
        return NULL;
    }

    PyArg_ParseTuple(args, "s", &reg);

    if (!strcmp(reg, "d"))
    {
        /* Read the port */
        outb(255, 0x37A);
        return Py_BuildValue("i", inb(0x378));
    }
    else if (!strcmp(reg, "s"))
    {
        /* Read the port */
        return Py_BuildValue("i", inb(0x379));
    }
    else if (!strcmp(reg, "c"))
    {
        /* Read the port */
        return Py_BuildValue("i", inb(0x37A));
    }
    else
    {
        printf("%s\n", "Please choose a valid register: d(ata), c(ontroll) or s(tatus)");
        Py_RETURN_NONE;
    }
}

static PyObject* writeport(PyObject* self, PyObject *args)
{
    /* Open registers */
    ioperm(0x378,1,1);
    ioperm(0x379,1,1);
    ioperm(0x37A,1,1);

    int val;
    char *reg;

    if (!PyArg_ParseTuple(args, "is", &val, &reg))
    {
        return NULL;
    }
    PyArg_ParseTuple(args, "is", &val, &reg);

    if (!strcmp(reg, "d"))
    {
        /* Set dataport to write mode */
        outb(0, 0x37A);
        /* Set the port */
        outb(val, 0x378);
    }
    else if (!strcmp(reg, "s"))
    {
        /* Set the port */
        outb(val, 0x379);
    }
    else if (!strcmp(reg, "c"))
    {
        /* Set the port */
        outb(val, 0x37A);
    }
    else
    {
        printf("%s\n", "Please choose a valid register: d(ata), c(ontroll) or s(tatus)");
    }
    Py_RETURN_NONE;
}


static char pyparport_docs[] = "Docs go here.\n";

static PyMethodDef pyparport_funcs[] = {
    {"read",    (PyCFunction)readport,  METH_VARARGS,   pyparport_docs},
    {"write",   (PyCFunction)writeport, METH_VARARGS,   pyparport_docs},
    {NULL}
};

void init_interface(void)
{
    Py_InitModule3("_interface", pyparport_funcs,
                    "Python parallel port object");
}
