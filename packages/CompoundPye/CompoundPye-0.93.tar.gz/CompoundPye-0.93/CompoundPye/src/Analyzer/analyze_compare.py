"""
@package CompoundPye.src.Analyzer.analyze_compare
Plot summation stage results of the Behnia-like ON pathway from several different
folders into one axis.
Also plots a few other plots to get a quick overview.
usage in ipython: run analyze_compare <path to folder containing output folders> <-log (optional, to set log-scale)> <--memory-friendly (optional, deletes Analyzer-objects after reading the required values)>
"""


import glob
import sys

import matplotlib.pyplot as plt
import analyzer as a
import numpy as np


class AnalyzeCompare:
    """
    
    """
    def __init__(self,path,memory_friendly=False):
        self.folders=glob.glob(path+'out*')
        self.folders.sort()
        self.speeds=np.array([float(fname.split('_')[-1]) for fname in self.folders])
        self.folders=[(self.speeds[i],self.folders[i]) for i in range(0,len(self.folders))]
        self.folders.sort()
        self.folders=[item[1] for item in self.folders]
        self.speeds.sort()
        
        self.memory_friendly=memory_friendly

        if not memory_friendly:
            self.ana_objects=[a.Analyzer(folder) for folder in self.folders]

        #self.max_lines=None
        #self.min_lines=None      

        self.name_of_loaded_neuron=None

    def get_max_min_lines(self,neuron_name='tangential HS',skip=0.4):

        if self.name_of_loaded_neuron!=neuron_name:

            max_lines=[]
            min_lines=[]
            mean_lines=[]

            if self.memory_friendly:

                for folder in self.folders:
                    ana=a.Analyzer(folder)
                    length=ana.neurons.shape[0]
                    max_lines.append(ana.neurons[neuron_name][int(skip*length):].max())
                    min_lines.append(ana.neurons[neuron_name][int(skip*length):].min())
                    mean_lines.append(ana.neurons[neuron_name][int(skip*length):].mean())
                    del ana

            else:
                length=self.ana_objects[0].neurons.shape[0]

                for ana in self.ana_objects:
                    max_lines.append(ana.neurons[neuron_name][int(skip*length):].max())
                    min_lines.append(ana.neurons[neuron_name][int(skip*length):].min())
                    mean_lines.append(ana.neurons[neuron_name][int(skip*length):].mean())


            max_lines=np.array(max_lines)
            min_lines=np.array(min_lines)
            mean_lines=np.array(mean_lines)

            '''
            print("="*20)
            print max_lines
            print min_lines
            print max_lines.max()
            print(min_lines.min())
            print("="*20)
            '''
            m=1
            m=max(abs(max_lines.max()),abs(min_lines.min()))
            #m=abs(max_lines.max())
            max_lines=max_lines/m
            min_lines=min_lines/m
            

            self.max_lines=max_lines
            self.min_lines=min_lines
            self.mean_lines=mean_lines

            return m
        else:
            return 1
    
    def plot_individuals(self,ax,plot_dict,plot_kwargs_excluding_color={},colors={}):
        """
        plot neurons' responses for simulations with different movement speeds
        idea: plot_dict={'one neurons name':[list,of,speed,indices],'another neurons name':[another,list,of,indices],...}
        """
        pass

    #def plot_max_min_resp(self,ax_max,ax_min,neuron_name,skip=0.4,scale='normal',plot_kwargs={'linestyle':'dashed','color':'blue','marker':'x','markersize':6,'mec':'black','mfc':'black','mew':3},normalize_0_to_max=False):
    def plot_max_resp(self,ax_max,neuron_name,scale='normal',plot_kwargs={'linestyle':'dashed','color':'blue','marker':'x','markersize':6,'mec':'black','mfc':'black','mew':3},normalize_0_to_1=False,min_max_speeds=[-360,360]):
        
        m=self.get_max_min_lines(neuron_name)

        max_lines=self.max_lines

        if normalize_0_to_1:
            x_max=max_lines.max()
            x_min=max_lines.min()
            a=1./(x_max-x_min)
            b=1-x_max*a
            max_lines=a*max_lines+b
                

        #if ax_max!=None:

        ind=np.where(((self.speeds*360<min_max_speeds[1]) & (self.speeds*360>=min_max_speeds[0])))[0]
        #print ind

        line,=ax_max.plot(self.speeds[ind]*360.,max_lines[ind],**plot_kwargs)
        
        ax_max.set_xlabel('Velocity [deg/s]',fontsize=17)
        ax_max.set_ylabel('Normalized maximum response',fontsize=17)

        if scale=='log':
            ax_max.set_xscale('log')


        return line,m

    def plot_min_resp(self,ax_min,neuron_name,scale='normal',plot_kwargs={'linestyle':'dashed','color':'blue','marker':'x','markersize':6,'mec':'black','mfc':'black','mew':3},normalize_0_to_1=False,min_max_speeds=[-360,360],possibly_invert=False):
        
        m=self.get_max_min_lines(neuron_name)

        min_lines=self.min_lines

        if normalize_0_to_1:
            x_max=min_lines.max()
            x_min=min_lines.min()
            a=1./(x_max-x_min)
            b=1-x_max*a
            min_lines=a*min_lines+b
                

        #if ax_min!=None:

        ind=np.where(((self.speeds*360<min_max_speeds[1]) & (self.speeds*360>=min_max_speeds[0])))[0]

        
        ind.sort()
        
        line,=ax_min.plot(self.speeds[ind]*360.,min_lines[ind],**plot_kwargs)
        
        ax_min.set_xlabel('Velocity [deg/s]',fontsize=17)
        ax_min.set_ylabel('Normalized response',fontsize=17)

        if scale=='log':
            ax_min.set_xscale('log')


        if min_lines.min()<0 and possibly_invert==True:
            ax_min.invert_yaxis()


        return line,m

    def plot_abs_max_resp(self,ax,neuron_name,scale='normal',plot_kwargs={'linestyle':'dashed','color':'blue','marker':'x','markersize':6,'mec':'black','mfc':'black','mew':3},min_max_speeds=[-360,360]):
        m=self.get_max_min_lines(neuron_name)

        abs_max=[]

        for i in range(len(self.max_lines)):
            if abs(self.max_lines[i])>abs(self.min_lines[i]):
                abs_max.append(self.max_lines[i])
            else:
                abs_max.append(self.min_lines[i])

        abs_max=np.array(abs_max)

        ind=np.where(((self.speeds*360<min_max_speeds[1]) & (self.speeds*360>=min_max_speeds[0])))[0]



        line,=ax.plot(self.speeds[ind]*360.,abs_max[ind],**plot_kwargs)
        
        ax.set_xlabel('Velocity [deg/s]',fontsize=17)
        ax.set_ylabel('Normalized maximum response',fontsize=17)

        if scale=='log':
            ax.set_xscale('log')

        return line,m


    def plot_mean_resp(self,ax,neuron_name,scale='normal',plot_kwargs={'linestyle':'dashed','color':'blue','marker':'x','markersize':6,'mec':'black','mfc':'black','mew':3},min_max_speeds=[-360,360]):
        m=self.get_max_min_lines(neuron_name)

        means=[]

        for i in range(len(self.max_lines)):
            if abs(self.max_lines[i])>abs(self.min_lines[i]):
                means.append(self.mean_lines[i])
            else:
                means.append(self.mean_lines[i])

        means=np.array(means)

        ind=np.where(((self.speeds*360<min_max_speeds[1]) & (self.speeds*360>=min_max_speeds[0])))[0]



        line,=ax.plot(self.speeds[ind]*360.,means[ind],**plot_kwargs)
        
        ax.set_xlabel('Velocity [deg/s]',fontsize=17)
        ax.set_ylabel('mean response',fontsize=17)

        if scale=='log':
            ax.set_xscale('log')

        return line,m
