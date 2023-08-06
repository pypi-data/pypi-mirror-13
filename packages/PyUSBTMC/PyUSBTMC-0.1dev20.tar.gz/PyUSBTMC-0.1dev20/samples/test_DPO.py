#
import PyUSBTMC,time

def set_record_length(self,recl):
    #recl:100,10000,100000,5000000 for DPO3k(?)
    #recl:100,10000,100000,10000000,20000000 for DPO4k 
    self.write("HOR:RECO %d"%recl)
    self.write("WFMINPRE:NR_PT %d"%recl)
    self.write(":DATA:START 1;")
    self.write(":DATA:STOP %d;"%recl)


def test_n(osc,n):
    print "RECL:",n
    osc.write(":ACQ:STATE STOP;")
    set_record_length(osc,n)
    time.sleep(1.0)
    osc.write(":ACQ:STATE RUN;")
    time.sleep(1.0)
    osc.write(":ACQ:STATE STOP;")
    st=time.time()
    osc.write("CURVE?")
    n,wf=osc.read(n+20)
    en=time.time()
    print n,len(wf.tostring()),en-st,n/(en-st)
    time.sleep(1)


if __name__ == "__main__":
    devs=PyUSBTMC.USB488_device.find_all()
    osc=devs[0]
    
    for n in (100000, 10**6, 10**7,2*10**7):
        test_n(osc,n)

    
