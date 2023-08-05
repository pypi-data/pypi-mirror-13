
.. code:: python

    from __future__ import print_function
    %matplotlib inline
    import fluidsim

.. _tutosimuluser:

Tutorial: running a simulation (user perspective)
=================================================

In this tutorial, I'm going to show how to run a simple simulation with
a solver that solves the 2 dimensional Navier-Stokes equations. I'm also
going to present some useful concepts and objects used in FluidSim.

A minimal simulation
--------------------

Fisrt, let's see what is needed to run a very simple simulation. For the
initialization (with default parameters):

.. code:: python

    from fluidsim.solvers.ns2d.solver import Simul
    params = Simul.create_default_params()
    sim = Simul(params)


.. parsed-literal::

    *************************************
    Program FluidDyn
    
    solver NS2D, RK4 and sequential,
    type fft: FFTWCY
    nx =     48 ; ny =     48
    Lx = 8. ; Ly = 8.
    path_run =
    /home/pierre/Sim_data/NS2D_L=8.x8._48x48_2015-06-26_13-41-13
    init_fields.type: constant
    Initialization outputs:
    <class 'fluidsim.base.output.increments.Increments'> increments
    <class 'fluidsim.base.output.phys_fields.PhysFieldsBase'> phys_fields
    <class 'fluidsim.solvers.ns2d.output.spectra.SpectraNS2D'> spectra
    <class 'fluidsim.solvers.ns2d.output.spatial_means.SpatialMeansNS2D'> spatial_means
    <class 'fluidsim.solvers.ns2d.output.spect_energy_budget.SpectralEnergyBudgetNS2D'> spect_energy_budg
    
    Memory usage at the end of init. (equiv. seq.): 71.0546875 Mo
    Size of state_fft (equiv. seq.): 0.0192 Mo


And then to run the simulation:

.. code:: python

    sim.time_stepping.start()


.. parsed-literal::

    *************************************
    Beginning of the computation
    save state_phys in file state_phys_t=000.000_it=0.hd5
        compute until t =         10
    it =      0 ; t =          0 ; deltat  =   0.083333
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
    
    it =      6 ; t =    1.08333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =     0.194 s
    it =     12 ; t =    2.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =     0.128 s
    it =     17 ; t =    3.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =     0.149 s
    it =     22 ; t =    4.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =    0.0996 s
    it =     27 ; t =    5.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =     0.113 s
    it =     32 ; t =    6.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =    0.0741 s
    it =     37 ; t =    7.28333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =    0.0435 s
    it =     43 ; t =    8.48333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =    0.0202 s
    it =     49 ; t =    9.68333 ; deltat  =        0.2
                  energy = 0.000e+00 ; Delta energy = +0.000e+00
                  estimated remaining duration =   0.00476 s
    Computation completed in 0.194266 s
    path_run =
    /home/pierre/Sim_data/NS2D_L=8.x8._48x48_2015-06-26_13-41-13
    save state_phys in file state_phys_t=010.083_it=51.hd5


In the following, we are going to understand these 4 lines of code...
But first let's clean-up by deleting the result directory of this tiny
example simulation:

.. code:: python

    import shutil
    shutil.rmtree(sim.output.path_run)

Importing a solver
------------------

The first line imports a "Simulation" class from a "solver" module. Any solver module has to provide a class called "Simul". We have already seen that the Simul class can be imported like this:

.. code:: python

    from fluidsim.solvers.ns2d.solver import Simul

but there is another convenient way to import it from a string:

.. code:: python

    Simul = fluidsim.import_simul_class_from_key('ns2d')

Create an instance of the class Parameters
------------------------------------------

The next step is to create an object ``params`` from the information
contained in the class ``Simul``:

.. code:: python

    params = Simul.create_default_params()

The object ``params`` is an instance of the class :class:`fluidsim.base.params.Parameters` (which inherits from `fluiddyn.util.paramcontainer.ParamContainer <http://fluiddyn.readthedocs.org/en/latest/generated/fluiddyn.util.paramcontainer.html>`_). It is usually a quite complex object containing many attributes. In this case, it contains many parameters. To print them, the normal way would be to use the tab-completion of Ipython, i.e. to type "`params.`" and press on the tab key. Here, I can not do that so I'm going to use a command that produce a list with the interesting attributes. If you don't understand this command, you should have a look at the section on `list comprehensions <https://docs.python.org/2/tutorial/datastructures.html#list-comprehensions>`_ of the official Python tutorial):

.. code:: python

    [attr for attr in dir(params) if not attr.startswith('_')]




.. parsed-literal::

    ['FORCING',
     'NEW_DIR_RESULTS',
     'ONLY_COARSE_OPER',
     'beta',
     'forcing',
     'init_fields',
     'nu_2',
     'nu_4',
     'nu_8',
     'nu_m4',
     'oper',
     'output',
     'short_name_type_run',
     'time_stepping']



and some useful functions (whose names all start with ``_`` in order to be hidden in Ipython): 

.. code:: python

    [attr for attr in dir(params) if attr.startswith('_') and not attr.startswith('__')]




.. parsed-literal::

    ['_attribs',
     '_load_from_elemxml',
     '_load_from_hdf5_file',
     '_load_from_hdf5_objet',
     '_load_from_xml_file',
     '_make_dict',
     '_make_element_xml',
     '_make_xml_text',
     '_print_as_xml',
     '_save_as_hdf5',
     '_save_as_xml',
     '_set_as_child',
     '_set_attrib',
     '_set_attribs',
     '_set_child',
     '_set_internal_attr',
     '_tag',
     '_tag_children']



Some of the attributes of ``params`` are simple Python objects and others can be other :class:`fluidsim.base.params.Parameters`:

.. code:: python

    print(type(params.nu_2))
    print(type(params.output))


.. parsed-literal::

    <type 'float'>
    <class 'fluidsim.base.params.Parameters'>


.. code:: python

    [attr for attr in dir(params.output) if not attr.startswith('_')]




.. parsed-literal::

    ['HAS_TO_SAVE',
     'ONLINE_PLOT_OK',
     'increments',
     'period_refresh_plots',
     'periods_plot',
     'periods_print',
     'periods_save',
     'phys_fields',
     'spatial_means',
     'spect_energy_budg',
     'spectra',
     'sub_directory']



We see that the object ``params`` contains a tree of parameters. This
tree can be represented as xml code:

.. code:: python

    print(params)


.. parsed-literal::

    <fluidsim.base.params.Parameters object at 0x7f8c52e034d0>
    
    <params ONLY_COARSE_OPER="False" short_name_type_run="" beta="0.0" nu_2="0.0"
            NEW_DIR_RESULTS="True" nu_4="0.0" nu_8="0.0" FORCING="False"
            nu_m4="0.0">
      <oper type_fft="FFTWCY" nx="48" ny="48" coef_dealiasing="0.6666666666666666"
            TRANSPOSED_OK="True" Lx="8" Ly="8"/>  
    
      <init_fields available_types="['from_file', 'noise', 'constant', 'jet',
                   'manual', 'dipole', 'from_simul']" type="constant">
        <from_file path=""/>  
    
        <noise length="0" velo_max="1.0"/>  
    
        <constant value="1.0"/>  
    
      </init_fields>
    
      <forcing nkmax_forcing="5" nkmin_forcing="4" key_forced="rot_fft"
               available_types="['proportional', 'random']" type=""
               forcing_rate="1">
        <random type_normalize="2nd_degree_eq"
                time_correlation="based_on_forcing_rate"/>  
    
      </forcing>
    
      <time_stepping type_time_scheme="RK4" it_end="10" USE_CFL="True" deltat0="0.2"
                     t_end="10.0" USE_T_END="True"/>  
    
      <output period_refresh_plots="1" HAS_TO_SAVE="True" ONLINE_PLOT_OK="True"
              sub_directory="">
        <periods_plot phys_fields="0"/>  
    
        <periods_print print_stdout="1.0"/>  
    
        <increments HAS_TO_PLOT_SAVED="False"/>  
    
        <spectra HAS_TO_PLOT_SAVED="False"/>  
    
        <spatial_means HAS_TO_PLOT_SAVED="False"/>  
    
        <spect_energy_budg HAS_TO_PLOT_SAVED="False"/>  
    
        <phys_fields field_to_plot="rot" file_with_it="False"/>  
    
        <periods_save spect_energy_budg="0" spatial_means="0" spectra="0"
                      increments="0" phys_fields="0"/>  
    
      </output>
    
    </params>
    


Set the parameters for your simulation
--------------------------------------

The user can change any parameters

.. code:: python

    params.nu_2 = 1e-3
    params.FORCING = False
    
    params.init_fields.type = 'noise'
    
    params.output.periods_save.spatial_means = 1.
    params.output.periods_save.spectra = 1.

but it is impossible to create accidentally a parameter which is actually not used:

.. code:: python

    try:
        params.this_param_does_not_exit = 10
    except AttributeError as e:
        print('AttributeError:', e)


.. parsed-literal::

    AttributeError: this_param_does_not_exit is not already set in params.
    The attributes are: set(['ONLY_COARSE_OPER', 'short_name_type_run', 'beta', 'nu_2', 'NEW_DIR_RESULTS', 'nu_4', 'nu_8', 'FORCING', 'nu_m4'])
    To set a new attribute, use _set_attrib or _set_attribs.


This behaviour is much safer than using a text file or a python file for
the parameters. In order to discover the different parameters for a
solver, create the ``params`` object containing the default parameters
in Ipython (``params = Simul.create_default_params()``), print it and
use the auto-completion (for example writting ``params.`` and pressing
on the tab key).

Instantiate a simulation object
-------------------------------

The next step is to create a simulation object (an instance of the class
solver.Simul) with the parameters in ``params``:

.. code:: python

    sim = Simul(params)


.. parsed-literal::

    *************************************
    Program FluidDyn
    
    solver NS2D, RK4 and sequential,
    type fft: FFTWCY
    nx =     48 ; ny =     48
    Lx = 8. ; Ly = 8.
    path_run =
    /home/pierre/Sim_data/NS2D_L=8.x8._48x48_2015-06-26_13-41-14
    init_fields.type: noise
    Initialization outputs:
    <class 'fluidsim.base.output.increments.Increments'> increments
    <class 'fluidsim.base.output.phys_fields.PhysFieldsBase'> phys_fields
    <class 'fluidsim.solvers.ns2d.output.spectra.SpectraNS2D'> spectra
    <class 'fluidsim.solvers.ns2d.output.spatial_means.SpatialMeansNS2D'> spatial_means
    <class 'fluidsim.solvers.ns2d.output.spect_energy_budget.SpectralEnergyBudgetNS2D'> spect_energy_budg
    
    Memory usage at the end of init. (equiv. seq.): 73.3515625 Mo
    Size of state_fft (equiv. seq.): 0.0192 Mo


which initializes everything needed to run the simulation. The object
``sim`` has a limited number of attributes:

.. code:: python

    [attr for attr in dir(sim) if not attr.startswith('_')]




.. parsed-literal::

    ['InfoSolver',
     'compute_freq_diss',
     'create_default_params',
     'info',
     'info_solver',
     'init_fields',
     'name_run',
     'oper',
     'output',
     'params',
     'state',
     'tendencies_nonlin',
     'time_stepping']



In the tutorial `Understand how works FluidSim <tuto_dev.html>`_, we will see what are all these attributes.

The object ``sim.info`` is a :class:`fluiddyn.util.paramcontainer.ParamContainer` which contains all the information on the solver (in ``sim.info.solver``) and on specific parameters for this simulation (in ``sim.info.solver``):

.. code:: python

    print(sim.info.__class__)
    print([attr for attr in dir(sim.info) if not attr.startswith('_')])


.. parsed-literal::

    <class 'fluiddyn.util.paramcontainer.ParamContainer'>
    ['params', 'solver']


.. code:: python

    sim.info.solver is sim.info_solver




.. parsed-literal::

    True



.. code:: python

    sim.info.params is sim.params




.. parsed-literal::

    True



.. code:: python

    print(sim.info.solver)


.. parsed-literal::

    <fluidsim.solvers.ns2d.solver.InfoSolverNS2D object at 0x7f8c52e03090>
    
    <solver class_name="Simul" module_name="fluidsim.solvers.ns2d.solver"
            short_name="NS2D">
      <classes>
        <Operators class_name="OperatorsPseudoSpectral2D"
                   module_name="fluidsim.operators.operators"/>  
    
        <InitFields class_name="InitFieldsNS2D"
                    module_name="fluidsim.solvers.ns2d.init_fields">
          <classes>
            <from_file class_name="InitFieldsFromFile"
                       module_name="fluidsim.base.init_fields"/>  
    
            <noise class_name="InitFieldsNoise"
                   module_name="fluidsim.solvers.ns2d.init_fields"/>  
    
            <constant class_name="InitFieldsConstant"
                      module_name="fluidsim.base.init_fields"/>  
    
            <jet class_name="InitFieldsJet"
                 module_name="fluidsim.solvers.ns2d.init_fields"/>  
    
            <manual class_name="InitFieldsManual"
                    module_name="fluidsim.base.init_fields"/>  
    
            <dipole class_name="InitFieldsDipole"
                    module_name="fluidsim.solvers.ns2d.init_fields"/>  
    
            <from_simul class_name="InitFieldsFromSimul"
                        module_name="fluidsim.base.init_fields"/>  
    
          </classes>
    
        </InitFields>
    
        <TimeStepping class_name="TimeSteppingPseudoSpectral"
                      module_name="fluidsim.base.time_stepping.pseudo_spect_cy"/>  
    
        <State keys_linear_eigenmodes="['rot_fft']" keys_state_fft="['rot_fft']"
               class_name="StateNS2D" keys_phys_needed="['rot']"
               keys_state_phys="['ux', 'uy', 'rot']"
               module_name="fluidsim.solvers.ns2d.state" keys_computable="[]"/>  
    
        <Output class_name="Output" module_name="fluidsim.solvers.ns2d.output">
          <classes>
            <PrintStdOut class_name="PrintStdOutNS2D"
                         module_name="fluidsim.solvers.ns2d.output.print_stdout"/>  
    
            <increments class_name="Increments"
                        module_name="fluidsim.base.output.increments"/>  
    
            <PhysFields class_name="PhysFieldsBase"
                        module_name="fluidsim.base.output.phys_fields"/>  
    
            <Spectra class_name="SpectraNS2D"
                     module_name="fluidsim.solvers.ns2d.output.spectra"/>  
    
            <spatial_means class_name="SpatialMeansNS2D"
                           module_name="fluidsim.solvers.ns2d.output.spatial_means"/>  
    
            <spect_energy_budg class_name="SpectralEnergyBudgetNS2D"
                               module_name="fluidsim.solvers.ns2d.output.spect_energy_budget"/>  
    
          </classes>
    
        </Output>
    
        <Forcing class_name="ForcingNS2D"
                 module_name="fluidsim.solvers.ns2d.forcing">
          <classes>
            <proportional class_name="Proportional"
                          module_name="fluidsim.base.forcing.specific"/>  
    
            <random class_name="TimeCorrelatedRandomPseudoSpectral"
                    module_name="fluidsim.base.forcing.specific"/>  
    
          </classes>
    
        </Forcing>
    
      </classes>
    
    </solver>
    


We see that a solver is defined by the classes it uses for some tasks. The tutorial `Understand how works FluidSim <tuto_dev.html>`_ is meant to explain how.

Run the simulation
------------------

We can now start the time stepping. Since
``params.time_stepping.USE_T_END is True``, it should loop until
``sim.time_stepping.t`` is equal or larger than
``params.time_stepping.t_end = 10``.

.. code:: python

    sim.time_stepping.start()


.. parsed-literal::

    *************************************
    Beginning of the computation
    save state_phys in file state_phys_t=000.000_it=0.hd5
        compute until t =         10
    it =      0 ; t =          0 ; deltat  =   0.097144
                  energy = 9.159e-02 ; Delta energy = +0.000e+00
    
    it =     11 ; t =    1.09076 ; deltat  =    0.10203
                  energy = 9.061e-02 ; Delta energy = -9.864e-04
                  estimated remaining duration =     0.216 s
    it =     21 ; t =     2.1292 ; deltat  =     0.1043
                  energy = 8.968e-02 ; Delta energy = -9.244e-04
                  estimated remaining duration =     0.265 s
    it =     31 ; t =    3.16728 ; deltat  =    0.10186
                  energy = 8.878e-02 ; Delta energy = -9.062e-04
                  estimated remaining duration =     0.212 s
    it =     41 ; t =    4.17421 ; deltat  =   0.099527
                  energy = 8.792e-02 ; Delta energy = -8.558e-04
                  estimated remaining duration =     0.201 s
    it =     52 ; t =    5.25129 ; deltat  =   0.099822
                  energy = 8.704e-02 ; Delta energy = -8.819e-04
                  estimated remaining duration =     0.151 s
    it =     62 ; t =    6.29295 ; deltat  =    0.10683
                  energy = 8.622e-02 ; Delta energy = -8.137e-04
                  estimated remaining duration =     0.138 s
    it =     72 ; t =    7.35239 ; deltat  =    0.10687
                  energy = 8.544e-02 ; Delta energy = -7.870e-04
                  estimated remaining duration =    0.0827 s
    it =     82 ; t =    8.44874 ; deltat  =    0.10722
                  energy = 8.466e-02 ; Delta energy = -7.756e-04
                  estimated remaining duration =    0.0502 s
    it =     92 ; t =    9.49721 ; deltat  =    0.10258
                  energy = 8.395e-02 ; Delta energy = -7.088e-04
                  estimated remaining duration =    0.0158 s
    Computation completed in 0.344521 s
    path_run =
    /home/pierre/Sim_data/NS2D_L=8.x8._48x48_2015-06-26_13-41-14
    save state_phys in file state_phys_t=010.010_it=97.hd5


Analyze the output
------------------

Let's see what we can do with the object ``sim.output``. What are its
attributes?

.. code:: python

    [attr for attr in dir(sim.output) if not attr.startswith('_')]




.. parsed-literal::

    ['compute_energy',
     'compute_energy_fft',
     'compute_enstrophy',
     'compute_enstrophy_fft',
     'create_list_for_name_run',
     'end_of_simul',
     'figure_axe',
     'has_been_initialized_with_state',
     'has_to_save',
     'increments',
     'init_with_initialized_state',
     'init_with_oper_and_state',
     'name_run',
     'name_solver',
     'one_time_step',
     'oper',
     'params',
     'path_run',
     'phys_fields',
     'print_size_in_Mo',
     'print_stdout',
     'sim',
     'spatial_means',
     'spect_energy_budg',
     'spectra',
     'sum_wavenumbers']



Many of these objects (``print_stdout``, ``phys_fields``,
``spatial_means``, ``spect_energy_budg``, ``spectra``, ...) were used
during the simulation to save outputs. They can also load the data and
produce some simple plots. For example, to display the time evolution of
spatially averaged quantities (here the energy, the entrophy and their
dissipation rate):

.. code:: python

     sim.output.spatial_means.plot()



.. image:: tuto_user_files/tuto_user_52_0.png



.. image:: tuto_user_files/tuto_user_52_1.png


Finally we remove the directory of this example simulation...

.. code:: python

    shutil.rmtree(sim.output.path_run)
