//  24 May 2014
//  Daniel Perron
//
// Use At your own risk

// 26 Dec 2015
// Gladkikh Artem
// Python Wrapper

//#define GPIO_BASE                0x20200000 /* GPIO controller */
#define GPIO_BASE                0x3f200000 /* GPIO controller */

#include "Python.h"
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <sched.h>

#define PAGE_SIZE (4*1024)
#define BLOCK_SIZE (4*1024)

int  mem_fd;
void *gpio_map;

// I/O access
volatile unsigned *gpio;


// GPIO setup macros. Always use INP_GPIO(x) before using OUT_GPIO(x) or SET_GPIO_ALT(x,y)
#define INP_GPIO(g) *(gpio+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio+((g)/10)) |=  (1<<(((g)%10)*3))
#define SET_GPIO_ALT(g,a) *(gpio+(((g)/10))) |= (((a)<=3?(a)+4:(a)==4?3:2)<<(((g)%10)*3))

#define GPIO_SET *(gpio+7)  // sets   bits which are 1 ignores bits which are 0
#define GPIO_CLR *(gpio+10) // clears bits which are 1 ignores bits which are 0

#define GPIO_READ(g)  (*(gpio + 13) &= (1<<(g)))


#define DS18B20_SKIP_ROM 		0xCC
#define DS18B20_CONVERT_T 		0x44
#define DS18B20_MATCH_ROM               0x55
#define DS18B20_SEARCH_ROM		0XF0
#define DS18B20_READ_SCRATCHPAD         0xBE
#define DS18B20_WRITE_SCRATCHPAD        0x4E
#define DS18B20_COPY_SCRATCHPAD         0x48


unsigned char ScratchPad[9];
double  temperature;
int   resolution;

void setup_io();


unsigned short ArgResolution=0;
unsigned short ArgScan=0;
unsigned short ArgFile=0;
unsigned short ArgWaitTime=750;
char FileName[256];

int  DoReset(unsigned short bus_pin)
{
    int loop;
    
    INP_GPIO(bus_pin);
    
    
    usleep(10);
    
    INP_GPIO(bus_pin);
    OUT_GPIO(bus_pin);
    
    // pin low for 480 us
    GPIO_CLR=1<<bus_pin;
    usleep(480);
    INP_GPIO(bus_pin);
    usleep(60);
    if(GPIO_READ(bus_pin)==0)
    {
        usleep(420);
        return 1;
    }
    return 0;
}

#define DELAY1US  smalldelay();

volatile int loop3;
void  smalldelay(void)
{
    //usleep(1);
    volatile int loop2;
    for(loop2=0;loop2<300;loop2++);
}



void WriteByte(unsigned char value, unsigned short bus_pin)
{
    unsigned char Mask=1;
    int loop;
    
    for(loop=0;loop<8;loop++)
    {
        INP_GPIO(bus_pin);
        OUT_GPIO(bus_pin);
        GPIO_CLR= 1 <<bus_pin;
        
        if((value & Mask)!=0)
        {
            DELAY1US
            
            INP_GPIO(bus_pin);
            usleep(60);
            
        }
        else
        {
            usleep(60);
            INP_GPIO(bus_pin);
            usleep(1);
        }
        Mask*=2;
        usleep(60);
    }
    
    
    usleep(100);
}

void WriteBit(unsigned char value, unsigned short bus_pin)
{
    INP_GPIO(bus_pin);
    OUT_GPIO(bus_pin);
    GPIO_CLR=1 <<bus_pin;
    if(value)
    {
        DELAY1US
        INP_GPIO(bus_pin);
        usleep(60);
    }
    else
    {
        usleep(60);
        INP_GPIO(bus_pin);
        usleep(1);
    }
    usleep(60);
}





unsigned char ReadBit(unsigned short bus_pin)
{
    unsigned char rvalue=0;
    INP_GPIO(bus_pin);
    OUT_GPIO(bus_pin);
    // PIN LOW
    GPIO_CLR= 1 << bus_pin;
    DELAY1US
    // set INPUT
    INP_GPIO(bus_pin);
    DELAY1US
    DELAY1US
    DELAY1US
    if(GPIO_READ(bus_pin)!=0)
    rvalue=1;
    usleep(60);
    return rvalue;
}

unsigned char ReadByte(unsigned short bus_pin)
{
    
    unsigned char Mask=1;
    int loop;
    unsigned  char data=0;
    
    int loop2;
    
    
    for(loop=0;loop<8;loop++)
    {
        //  set output
        INP_GPIO(bus_pin);
        OUT_GPIO(bus_pin);
        //  PIN LOW
        GPIO_CLR= 1<<bus_pin;
        DELAY1US
        //  set input
        INP_GPIO(bus_pin);
        // Wait  2 us
        DELAY1US
        DELAY1US
        DELAY1US
        if(GPIO_READ(bus_pin)!=0)
        data |= Mask;
        Mask*=2;
        usleep(60);
    }
    
    return data;
}



int ReadScratchPad(unsigned short bus_pin)
{
    int loop;
    
    WriteByte(DS18B20_READ_SCRATCHPAD, bus_pin);
    for(loop=0;loop<9;loop++)
    {
        ScratchPad[loop]=ReadByte(bus_pin);
    }
}

unsigned char  CalcCRC(unsigned char * data, unsigned char  byteSize)
{
    unsigned char  shift_register = 0;
    unsigned char  loop,loop2;
    char  DataByte;
    
    for(loop = 0; loop < byteSize; loop++)
    {
        DataByte = *(data + loop);
        for(loop2 = 0; loop2 < 8; loop2++)
        {
            if((shift_register ^ DataByte)& 1)
            {
                shift_register = shift_register >> 1;
                shift_register ^=  0x8C;
            }
            else
            shift_register = shift_register >> 1;
            DataByte = DataByte >> 1;
        }
    }
    return shift_register;
}

char  IDGetBit(unsigned long long *llvalue, char bit)
{
    unsigned long long Mask = 1ULL << bit;
    
    return ((*llvalue & Mask) ? 1 : 0);
}


unsigned long long   IDSetBit(unsigned long long *llvalue, char bit, unsigned char newValue)
{
    unsigned long long Mask = 1ULL << bit;
    
    if((bit >= 0) && (bit < 64))
    {
        if(newValue==0)
        *llvalue &= ~Mask;
        else
        *llvalue |= Mask;
    }
    return *llvalue;
}


void SelectSensor(unsigned  long long ID, unsigned short bus_pin)
{
    int BitIndex;
    char Bit;
    
    
    WriteByte(DS18B20_MATCH_ROM,bus_pin);
    
    for(BitIndex=0;BitIndex<64;BitIndex++)
    WriteBit(IDGetBit(&ID,BitIndex), bus_pin);
    
}

int  SearchSensor(unsigned long long * ID, int * LastBitChange, unsigned short bus_pin)
{
    int BitIndex;
    char Bit , NoBit;
    
    
    if(*LastBitChange <0) return 0;
    
    // Set bit at LastBitChange Position to 1
    // Every bit after LastbitChange will be 0
    
    if(*LastBitChange <64)
    {
        
        IDSetBit(ID,*LastBitChange,1);
        for(BitIndex=*LastBitChange+1;BitIndex<64;BitIndex++)
        IDSetBit(ID,BitIndex,0);
    }
    
    *LastBitChange=-1;
    
    if(!DoReset(bus_pin)) return -1;
    
    
    WriteByte(DS18B20_SEARCH_ROM,bus_pin);
    
    for(BitIndex=0;BitIndex<64;BitIndex++)
    {
        NoBit = ReadBit(bus_pin);
        Bit = ReadBit(bus_pin);
        
        if(Bit && NoBit)
        return -2;
        
        if(!Bit && !NoBit)
        {
            // ok 2 possibilities
            //          printf("B");
            if(IDGetBit(ID,BitIndex))
            {
                // Bit High already set 
                WriteBit(1,bus_pin);
            }
            else
            {
                // ok let's try LOW value first
                *LastBitChange=BitIndex;
                WriteBit(0,bus_pin);
            }
        }
        else if(!Bit)
        { 
            //	printf("1");
            WriteBit(1,bus_pin);
            IDSetBit(ID,BitIndex,1);
        }
        else
        {
            //printf("0");
            WriteBit(0,bus_pin);
            IDSetBit(ID,BitIndex,0);
        }
        //   if((BitIndex % 4)==3)printf(" ");
    }
    //
    // printf("\n");
    return 1;
    
    
    
}







float ReadSensor(unsigned long long ID, unsigned short bus_pin)
{
    int RetryCount;
    int loop;
    unsigned char  CRCByte;
    union {
        short SHORT;
        unsigned char CHAR[2];
    }IntTemp;
    
    
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    
    temperature=-9999.9;
    
    for(RetryCount=0;RetryCount<10;RetryCount++)
    {
        if(!DoReset(bus_pin)) continue;

        // start a conversion
        SelectSensor(ID,bus_pin);
        
        if(!ReadScratchPad(bus_pin))
        {
            //printf("can't read");
            continue;
        }
        
            // for(loop=0;loop<9;loop++)
            //   printf("%02X ",ScratchPad[loop]);
            // printf("\n");fflush(stdout);
        
        // OK Check sum Check;
        CRCByte= CalcCRC(ScratchPad,8);
        
        if(CRCByte!=ScratchPad[8])
        {
            //printf("CRC error");
            continue;
        }
        
        //Check Resolution
        resolution=0;
        switch(ScratchPad[4])
        {
            
            case  0x1f: resolution=9;break;
            case  0x3f: resolution=10;break;
            case  0x5f: resolution=11;break;
            case  0x7f: resolution=12;break;
        }
        
        if(resolution==0)
        {
           //printf("no resolution");
            continue;
        }
        // Read Temperature
        
        IntTemp.CHAR[0]=ScratchPad[0];
        IntTemp.CHAR[1]=ScratchPad[1];
        
        
        temperature =  0.0625 * (double) IntTemp.SHORT;
        
        ID &= 0x00FFFFFFFFFFFFFFULL;
        //printf("%02llX-%012llX : ",ID & 0xFFULL, ID >>8);
        
        //printf("%02d bits  Temperature: %6.2f +/- %4.2f Celsius\n", resolution ,temperature, 0.0625 * (double)  (1<<(12 - resolution)));
        
        break;
    }
    
        return temperature;
    
}



int GlobalStartConversion(unsigned short bus_pin)
{
    DoReset(bus_pin);
    WriteByte(DS18B20_SKIP_ROM,bus_pin);
    WriteByte(DS18B20_CONVERT_T,bus_pin);
    return 1;
}


void WriteScratchPad(unsigned char TH, unsigned char TL, unsigned char config, unsigned short bus_pin)
{
    
    // First reset device
    
    DoReset(bus_pin);
    
    usleep(10);
    // Skip ROM command
    WriteByte(DS18B20_SKIP_ROM,bus_pin);
    
    
    // Write Scratch pad
    
    WriteByte(DS18B20_WRITE_SCRATCHPAD,bus_pin);
    
    // Write TH
    
    WriteByte(TH,bus_pin);
    
    // Write TL
    
    WriteByte(TL,bus_pin);
    
    // Write config
    
    WriteByte(config,bus_pin);
}


void  CopyScratchPad(unsigned short bus_pin)
{
    
    // Reset device
    DoReset(bus_pin);
    usleep(1000);
    
    // Skip ROM Command
    
    WriteByte(DS18B20_SKIP_ROM,bus_pin);
    
    //  copy scratch pad
    
    WriteByte(DS18B20_COPY_SCRATCHPAD,bus_pin);
    usleep(100000);
}



static unsigned long long sensors_arr[64];
static float sensors_vals[64];

void ScanForSensor(unsigned short bus_pin)
{
    unsigned long long  ID=0ULL;
    int  NextBit=64;
    int  _NextBit;
    int  rcode;
    int retry=0;
    int sensor_counter = 0;
    float temper;
    unsigned long long  _ID;
    unsigned char  _ID_CRC;
    unsigned char _ID_Calc_CRC;
    unsigned char  _ID_Family;
    
    int i;
    for(i = 0; i < 64; i++) sensors_arr[i] = 0;  //clear sensors array
    
    while(retry<30){
        _ID=ID;
        _NextBit=NextBit;
        rcode=SearchSensor(&_ID,&_NextBit,bus_pin);
        if(rcode==1)
        {
            _ID_CRC =  (unsigned char)  (_ID>>56);
            _ID_Calc_CRC =  CalcCRC((unsigned char *) &_ID,7);
            if(_ID_CRC == _ID_Calc_CRC)
            {
                temper = ReadSensor(_ID,bus_pin);
               if(temper > -65.5)
                {
                    sensors_vals[sensor_counter] = temper;
                    sensors_arr[sensor_counter++] = _ID;
                    ID=_ID;
                    NextBit=_NextBit;
                    retry=0;
                }
            }
            else 
            { 
                retry++;
            }
        }
        else if(rcode==0 )
        break;
        else
        retry++;
    }
}



// Adafruit   set_max_priority and set_default priority add-on

void set_max_priority(void) {
    struct sched_param sched;
    memset(&sched, 0, sizeof(sched));
    // Use FIFO scheduler with highest priority for the lowest chance of the kernel context switching.
    sched.sched_priority = sched_get_priority_max(SCHED_FIFO);
    sched_setscheduler(0, SCHED_FIFO, &sched);
}

void set_default_priority(void) {
    struct sched_param sched;
    memset(&sched, 0, sizeof(sched));
    // Go back to default scheduler with default 0 priority.
    sched.sched_priority = 0;
    sched_setscheduler(0, SCHED_OTHER, &sched);
}

//
// Set up a memory regions to access GPIO
//
void setup_io()
{
    /* open /dev/mem */
    if ((mem_fd = open("/dev/mem", O_RDWR|O_SYNC) ) < 0) {
        printf("can't open /dev/mem \n");
        exit(-1);
    }
    
    /* mmap GPIO */
    gpio_map = mmap(
    NULL,             //Any adddress in our space will do
    BLOCK_SIZE,       //Map length
    PROT_READ|PROT_WRITE|PROT_EXEC,// Enable reading & writting to mapped memory
    MAP_SHARED,       //Shared with other processes
    mem_fd,           //File to map
    GPIO_BASE         //Offset to GPIO peripheral
    );
    
    close(mem_fd); //No need to keep mem_fd open after mmap
    
    if (gpio_map == MAP_FAILED) {
        printf("mmap error %d\n", (int)gpio_map);//errno also set!
        exit(-1);
    }
    
    // Always use volatile pointer!
    gpio = (volatile unsigned *)gpio_map;
    
    
} // setup_io



static PyObject *ds18b20Error;

static PyObject *
py_search(PyObject *self, PyObject *args)
{
    int bus_pin;
    int i;
    
    if (!PyArg_ParseTuple(args, "i", &bus_pin))
    {
        PyErr_SetString(ds18b20Error, "integer GPIO should be provided.");
        return NULL;
    }    
    
    PyObject * dict = Py_BuildValue("{}");
    ScanForSensor(bus_pin);
    for(i = 0; i < 64; i++)
    {
        if(sensors_arr[i] != 0)
        {
            PyDict_SetItem(dict, Py_BuildValue("l", sensors_arr[i]), 
                                 Py_BuildValue("f", sensors_vals[i]));        
        }
    }
    return dict;
}

static PyObject *
py_convert(PyObject *self, PyObject *args)
{
    int bus_pin;
    unsigned long long id;
    int i;
    
    if (!PyArg_ParseTuple(args, "i", &bus_pin))
    {
        PyErr_SetString(ds18b20Error, "integer GPIO should be provided.");
        return NULL;
    }
    
    GlobalStartConversion(bus_pin);
    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef r2_ds18b20_funcs[] = {
    {"search", (PyCFunction)py_search, 
     METH_VARARGS, "search sensors on given GPIO"},
    {"convert", (PyCFunction)py_convert, 
     METH_VARARGS, "starts global conversion on given GPIO"},
    {NULL}
};


#if PY_MAJOR_VERSION >= 3
  #define MOD_ERROR_VAL NULL
  #define MOD_SUCCESS_VAL(val) val
  #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef);
#else
  #define MOD_ERROR_VAL
  #define MOD_SUCCESS_VAL(val)
  #define MOD_INIT(name) void init##name(void)
  #define MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
#endif


MOD_INIT(r2_ds18b20)
{
    setup_io();
    PyObject *m;
    
    MOD_DEF(m,"r2_ds18b20", "r2_ds18b20!", r2_ds18b20_funcs);
                   
    if (m == NULL)
        return MOD_ERROR_VAL;
                   
    ds18b20Error = PyErr_NewException("ds18b20.error", NULL, NULL);
    Py_INCREF(ds18b20Error);
    PyModule_AddObject(m, "error", ds18b20Error);
    return MOD_SUCCESS_VAL(m);
}