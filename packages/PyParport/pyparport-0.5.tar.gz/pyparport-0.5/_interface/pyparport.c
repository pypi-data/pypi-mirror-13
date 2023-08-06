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
    int addr;

    if (!PyArg_ParseTuple(args, "si", &reg, &addr))
    {
        return NULL;
    }

    PyArg_ParseTuple(args, "si", &reg, &addr);

    if (!strcmp(reg, "d"))
    {
        /* Set dataport to read mode */
        outb(255, addr+2);
        /* Read the port */
        return Py_BuildValue("i", inb(addr));
    }
    else if (!strcmp(reg, "s") | !strcmp(reg, "c"))
    {
        /* Read the port */
        return Py_BuildValue("i", inb(addr));
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
    int addr;

    if (!PyArg_ParseTuple(args, "isi", &val, &reg, &addr))
    {
        return NULL;
    }
    PyArg_ParseTuple(args, "isi", &val, &reg, &addr);

    if (!strcmp(reg, "d"))
    {
        /* Set dataport to write mode */
        outb(0, addr+2);
        /* Set the port */
        outb(val, addr);
    }
    else if (!strcmp(reg, "s") | !strcmp(reg, "c"))
    {
        /* Set the port */
        outb(val, addr);
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
