
This week, we're going to run an actual quantum
algorithm, the Deutsch Jozsa algorithm,
on a real quantum computer.
And of course, we'll first discuss in detail
how that works.
To do this, we'll need to introduce
the algorithm using a circuit model of quantum computation.
But before we do that, let's first
look at an example of a circuit model
in the context of classical computation.
The circuit model for classical computation
begins with input data prepared at the initialization stage.
We can think of the computational bits in the input
register being reset to all zeros
and then set to the initial values that
will be input to the computer.
Now, this reset step may not be absolutely
necessary in a classical computer.
But we'll include it here for comparison
with the quantum circuit model that we'll discuss later.
The initialized bits are then input to a computational stage.
Here, a series of logical operations
are implemented using classical Boolean logic gates to compute
a series of functions.
And once this is complete, the output for this stage
encodes the result of the computation.
For example, let's consider a full adder circuit
comprising a series of Boolean logic gates.
The full adder takes as inputs the bits B1 through B3.
Where B1 and B2 are the binary numbers we want to add
and B3 holds any carry in that we may have
from a previous calculation.
Here we don't have a carry forward so its value is zero.
An output of this circuit is the sum, B1 plus B2 modulo 2,
where the modulo 2 arises because this
is binary arithmetic.
The second output is the arithmetic
carry out that may result from the addition.
These two values are then assigned to bits B4 and B5
and stored in the output register.
In this case, we add 1 plus 1, which
is of course 2 with decimal numbers.
And for the binary addition performed by this circuit,
the addition is modulo 2, 1 plus 1 equals 0, and has
a carry forward of 1.
Finally, the results from this addition problem
are obtained in a measurement stage, where
the values of bits B4 and B5 are the binary representation
of the answer, which may be then converted back
to a decimal result.
This type of initialized, compute and measure process
is the foundation for a universal classical machine.
To access this machine, a user interface
provides the input data and the program instruction
set that will calculate a desired function.
This instruction set is then applied
to the physical hardware using a controller layer.
This layer takes the input data, sets the input bits,
implements the physical logic gates
according to the instruction set, measures the output,
and then sends the resulting data
back to the user interface.
This computational model illustrates the basic building
blocks that we'll need to implement an algorithm using
a quantum circuit model.
The main distinction will be the role of quantum mechanics
and its impact on the initialization, compute
and measurement stages.


In the last section, we introduced a circuit model
for classical computation.
This model included an initialization stage
to set the input bits, a compute stage that implemented
classical logic gates to compute a function,
and a measurement stage to extract the output.
In this section, we'll introduce an analogous circuit
model for quantum computation.
The basic structure is the same.
Initialize, compute, and measure.
We'll start with an initialization stage
where the qubits are first reset to state 0
and then initialized to their input values.
We'll assume here that the initial state is also 0, 0, 0.
The initialized qubits are then input to the computation stage
where a series of quantum logic operations will be performed.
In general, one of the first steps in this block
is to create an equal superposition state.
This is done by applying single qubit Hadamard
gates to the input register.
To see how this works, let's first
consider just a single qubit in state zero.
The Hadamard gate applied to this qubit takes state 0
and rotates it to an equal superposition state, 0 plus 1,
and the normalization constant is 1 over square root of 2.
Now what happens when we have two qubits each initialized
in states zero?
Applying a Hadamard gate to each one
independently rotates each into an equal superposition state
0 plus 1.
And when we take the tensor product effectively multiplying
out the terms, we find an equal superposition state
of 2 qubits, 0, 0 plus 0, 1 plus 1, 0 plus 1, 1.
And now the normalization is the square of 1
over root 2, which is 1/2.
Similarly, applying a Hadamard gate to three qubits,
each initialized in state zero, results
in an equal superposition state of three qubits.
As we've seen before, this state comprises eight terms,
from state 0, 0, 0 all the way to state 1, 1, 1.
And the normalization is now 1 over root 2 cubed.
And each coefficient now has this value.
Creating a large, equal superposition state
sets the stage for quantum parallelism and quantum
interference to occur during quantum logic operations.
The logic operations themselves are the single qubit
and two qubit gates we discussed earlier.
For example, a single qubit X gate or another Hadamard gate
or a two qubit CNOT gate, chosen to implement
a particular function or algorithm.
And as we saw in week one, the quantum parallelism and quantum
interference that occurred during these operations
changed the values of the coefficients
in the superposition state.
And finally, the qubits are then measured
to determine the answer.
And as we also saw earlier in the course,
the measurement process projects the qubits
onto the measurement basis.
This effectively collapses the massive superposition state
onto a single classical state with a probability that's
the magnitude squared of its coefficient.
In doing so, the measurement leads
to a single classical binary result, either a 0 or a 1
for each qubit.
Now if we don't perform any logic operations
and simply measure the equal superposition
state from the input, each coefficient has the same value
and we have an equal probability, one eighth,
of measuring any one of these states.
Thus as we discussed earlier in the course, to be successful,
a quantum algorithm is designed such
that after applying a designated sequence of quantum logic
gates, ideally, all of the probability amplitude
resides in one of the coefficients.
And this coefficient sits in front of the state
that encodes the answer to our problem.
Thus when we make a projective measurement,
the probability is unity that we obtain this result.
Using this basic quantum circuit model, initialize, compute,
and measure, we can implement a universal quantum algorithm.
And in the next section, we'll apply this model
to a specific example, the Deutsch-Jozsa algorithm.


In this section, we'll introduce the Deutsch-Jozsa Algorithm.
Deutsch-Jozsa was one of the first quantum algorithms
that exhibited a provable, exponential speed up
over a classical algorithm.
In this section, we'll learn how it works
and walk through its key steps.
And by the end of this week, you'll
implement it for yourselves on a real cloud based
quantum computer.
To get started, imagine that we have an unknown function f.
It takes N Bits as input, and it outputs a single result,
either a 0 or a 1.
Now, all we know about this function
is that it has a unique property.
It's either a constant function or it's a balanced function.
OK.
What do we mean by that?
Well, a constant function takes any input,
and no matter what that input may be, the function always
outputs the same result. For example, independent
of the input, the function always outputs
a zero, or no matter the input, it always outputs a one.
A balanced function, on the other hand,
will take those inputs, and for half of them,
we don't specify which half, but for half of them
it'll output a zero and for the other half it'll output a one.
In this sense, the output is balanced.
The Deutsch-Jozsa problem is the following.
Determine whether a function f is
constant or balanced based on queries that you
make of the function f.
You can send any input state to the function
and you get a result back, and you can query the function
as many times as you like.

Now for N Bits, there are two to the n-th power
different input states that you can choose from.
And you'll need to run the function for at least half
of them to determine with certainty if the function is
constant or balanced.

In fact, you'll have to do it for half plus one.
That's because even if you get all zeros for the first half
of the states you try, you'll need
to try one more just to see if the second half remains zeros,
a constant function, or all ones, a balanced function.
Thus, a deterministic classical algorithm
will take 2 to the N divided by 2 plus 1 steps.
And it always works.
Now, if you have N Qubits instead,
you can create an equal superposition state of all N
Qubits, and as we'll see, determine
the answer in just one step.
And it always works.
And that's an exponential speed up.
To see how this works in detail, let's simplify the problem
to just one bit or one qubit.
It's the same approach as for N Bits or N Qubits,
but it'll be much easier to follow if we just
take n equals to one.
In this case, for a constant function we have f of 0
equals f of 1 and the output is either a 0 for both of them,
or it's a one for both of them.
And for a balanced function, one of the outputs is 0
and the other is 1.
In the truth table, we can make the following observation,
that if we take the exclusive or of f of 0 and f of 1,
the result is 0 for a constant function
and it's 1 for a balanced function.
In this case, classically it takes two steps
to implement the algorithm for n equal one.
And again, quantum mechanically it only takes one step.
Now, that may not seem like a big speed up.
It's only twice as fast, but in fact, for N equal one,
it is an exponential speed up.
And this generalizes to any number N that you may choose.
Again, we're going with N equal one
because it'll be easier to see how the algorithm works.
To implement the Deutsch-Jozsa Algorithm for N equal 1,
we actually need two qubits.
One is the data qubit, that's the N equal one qubit,
and the other is a helper qubit or an ancilla qubit.
And we'll use the quantum circuit model
to implement this algorithm.
First, we initialize the qubits into their starting states.
The data qubit is prepared in state zero and the helper qubit
in state one.
As we proceed through the algorithm,
we'll indicate the position at each stage of the algorithm
and also the state of these two qubits.
For example, after initialization we
see that the data qubit is in state zero
and the helper qubit is in state one.
To keep it all straight we'll use
yellow to highlight the data qubit state and green
to highlight the helper qubit state.
We first create an equal superposition state
by applying a Hadamard gate to both qubits.
This results in a superposition state for each qubit.
There's a plus sign for the data qubit
since it started in state zero and a minus sign for the helper
qubit since it started in state one.
Next, we'll just expand out the terms in the data qubit.
The zero state tensor product, the helper qubit superposition
state plus one state tensor product, the helper qubit
state.
This state is then input into the quantum circuit block.
We'll just call it U sub f.
The data qubit is x and the helper qubit is y.
U sub f implements the set of logical operations.
And it does two things.
First, it implements the unknown function f,
and second, it outputs the exclusive or of bits
y and f of x.
We'll show later how this can be implemented with single qubit
and two qubit operations.
For now, though, let's just figure out what happens.
At the output of U sub f, we have the helper qubit.
And it takes on the state y, x, or f of x.
So where the data qubit is zero, the helper qubit
is x ord with f of 0.
And where the data qubit is one the helper qubit state
is x ord with f of 1.
Now we make an observation.
You should try this on scratch paper
to convince yourself that the expression can be written
in this way with a minus 1 to the f of 0 power and a minus 1
to the f of 1 power.
To check, there are four cases to consider.
For example, if f of x equals 0 for any x,
the x or expressions on the left maintain the superposition 0
minus 1.
However, if f of x equals 1 for any x,
then the x or expressions on the left result in 1 minus 0.
And to return this to the superposition state 0 minus 1,
we need to multiply by a minus 1.
This is achieved by taking minus 1 to the fx power.
And when fx equals 1, this is the minus one
that we're looking for.
The expression also works when f of 0 and f of 1
are not equal, but take on the values 0 and 1, the third case,
or 1 and zero, the fourth case.
The fact that this works for all four cases
simultaneously is an example of quantum parallelism.
In the next step we factor out the helper qubit term 0 minus 1
divided by root 2.
And we move the minus 1 to the f of 0 power and the minus 1
to the f of 1 power over to the data qubit.
Next, we apply Hadamard gates to the data and helper qubits.
On the data qubit, state zero rotates to 0 plus 1
and state 1 rotates to 0 minus 1.
For the helper qubit, 0 minus 1 rotates to state 1.
Next, we just note that minus 1 to the f of x power
is the same as e to the power minus i pi f of x.
And then we just rearrange terms to collect
the coefficients of state zero and the coefficients of state
one.
And this is an example of where quantum interference occurs,
changing the values of the coefficients
depending on whether the function is
constant or balanced.
For example, if f of 0 equals f of 1,
a constant function, then b equals 0 and a
is either plus or minus 1.
Thus, a measurement will yield state 0 with unity probability.
And we observe that state zero is equivalent to state f of 0,
x ord with f of 1.
In contrast, if f of 0 does not equal f of 1,
a balanced function, then a equals 0 and b
is plus or minus 1.
In this case, a measurement will yield state one
with unity probability.
And we observe that state one can also
be replaced with the state f of 0, x or f of 1.
Thus, if we measure a 0 on the data qubit,
the function is constant, but if we measure a 1
on the data qubit, the function is balanced, and we’ll always
measure a state one on the helper qubit.
And so with one evaluation of the quantum algorithm
we were able to determine whether the function was
constant or balanced.
And the same is true if we had instead used N data qubits.
One evaluation always works.
In contrast, the classical case must evaluate half of the 2
to the N states plus one to get a deterministic answer.
And so the quantum speed up is one step versus 2
to the N minus 1 plus 1 steps.
Lastly, we can look at ways to implement the logical operation
U sub f.
I won't talk through all of them here.
You can find them in the text unit following this video.
But there are four cases corresponding
to the two constant functions 0, 0 and 1, 1,
and the two balanced functions 0, 1 and 1, 0.
I encourage you to work through each of these cases.
Now that we understand how the Deutsch-Jozsa Algorithm works
within the quantum circuit model,
we're ready to write a quantum computer
program that will implement it on a quantum computer.
And we'll see how that generally is done in the next section,
and then more specifically in the lab practicum.


Like classical computers, quantum computers
have a software stack used in the development of programs,
analysis of designs, and testing of constructive programs
and circuits.
The function and examples of these quantum software tools
is a topic of this section.
Let's start by contrasting quantum software tools
to classical ones to perform similar types of functions.
To create a classical circuit design,
one may use a schematic capture CAD tool.
A quantum analog to this is the circuit composer
from IBM's quantum experience.
For program based designs, for example,
HDL circuit designs written in VHDL or Verilog,
or high level computer programs written in a language like c++,
one uses a compiler to translate the program to a lower level
format.
Numerous quantum compilers exist that perform the same function.
Some examples include Quipper developed
by Dalhousie University and Q sharp from Microsoft.
These quantum compilers typically
produce an intermediate format known as QASM,
or quantum assembly language.
Finally, to translate a program or circuit to a format
that a machine can execute, one uses an assembler.
A similar function is required for quantum circuits.
Each hardware platform will have specific gates
that it can execute, and the connectivity that it provides
is specific to the topology constraints of the technology.
Mapping from QASM programs to hardware
is something that IBM's QISKit software
performs, in this case, for superconductor
based technology.
For classical circuit designs, a circuit simulation tool
like Spice is commonly used to determine circuit properties
like power consumption, timing, and to verify
correctness of the circuit.
For quantum circuits, one of the main concerns
is how noise or errors impact the operation of the circuit.
Quantum simulation tools exist at multiple levels
of abstraction that model air in the operation
of quantum circuits.
Quantum assimilation tools are also
used to calculate the fidelity of gates operating
under the control of control waveforms,
and to verify correctness of circuits.
The last category of tools are those used
for testing of fabricated chips, PCBs, et cetera.
For classical chips, one may use hardware and software tools,
such as JTAG and boundary scan to verify
the operation of a chip.
For quantum circuits, quantum characterization, validation,
and verification, or QCVV tools provide a similar function.
These tools evaluate results obtained from experimental runs
to calculate the Fidelity devices
and to verify their correctness.
Let's now talk about the main steps
one would use to program a quantum computer.
Program generation, hardware specific circuit mapping,
and hardware control and execution.
The program generation phase is hardware agnostic,
whereas the other two phases deal
with aspects that are specific to the architecture
of the hardware platform.
Another difference between quantum computing systems
and classical ones is that the control and processing
systems are typically separate.
There is a classical system for control,
and a quantum device for processing.
In many cases, these two systems are physically separated.
For example, a superconducting quantum computer
may use room temperature instruments for control,
whereas the quantum circuits require millikelvin
temperatures, and must be located within a dilution
refrigerator.
Let's now look at the three main methods
for program generation, the first being schematic capture.
One of the front ends to IBM's quantum experience,
the composer tool is an example of a schematic capture
tool, where one uses a GUI to construct a circuit consisting
of one and two qubit gates and measurements.
The tool knows of underlying hardware constraints,
and prevents the user from violating these.
In many cases, it is more convenient to specify
the quantum circuit as a program, which
allows for the specification of larger scale circuits.
This leads to the motivation behind the second method
for program generation, high level quantum languages.
Examples of this are tools like Quipper, Q Sharp, and Scaffold.
High level programs written in these languages
are compiled into QASM circuits, or can be
displayed as circuit diagrams.
The last method for program generation that we will discuss
is problem specific generation.
Google's Open Fermion software tool
is an example of this method.
This particular package is designed specifically
for formulating simulations of quantum chemistry.
An advantage of this approach is that it
incorporates the steps and the known methods used
for the particular class of problems,
without requiring the user to know detailed domain knowledge
or the methods used to solve these problems.
A user specifies a problem at a high level,
and the package generates a quantum circuit
that can be mapped to a hardware specific platform or simulation systems.
And so we have seen the type of software tools
that are commonly used to program a quantum computer,
and how these tools are similar to tools
used for classical computers.
In the next section, we'll look at other types of software
used in the control, design, and testing of quantum computers.


As you saw previously, a quantum computer
requires a classical control system.
For small to medium sized quantum computers,
the control can be realized using commercially available
instruments-- for example, arbitrary waveform
generators, microwave sources, and laser systems.
Software is required to program and synchronize
the various instruments required.
Labber is one example of this type of software.
This software also provides a result visualization
and logging functions.
Quantum computer control systems that are custom designs
require firmware and software control software.
IBM's QISKit for superconducting circuits and ARTIQ
for ion traps are examples of these types of software control
systems.
Additionally, and especially for small scale experiments,
many experimental groups use homegrown software control
systems.
Let's now discuss hardware testing and validation
of quantum systems, which is typically
performed with the aid of analysis techniques
and software known as QCVV, Quantum Characterization,
Verification, and Validation.
These techniques take the results
of a sequence of experiments and produce descriptive metrics,
like gate fidelity or operator descriptions of the underlying
gates.
Two of the most popular techniques in use
today are randomized benchmarking and gate
set tomography.
In randomized benchmarking, an experiment
consists of a long sequences of repeated target
gate interspersed with random other gates.
The random gates essentially randomize the error
seen in the target gate and allow
us to calculate the average fidelity of this target gate.
This procedure also mitigates the impact
that imperfect state preparation and measurement
have on the fidelity.
One of the disadvantages of randomized benchmarking
is that it only provides a single metric for the gate--
namely, the fidelity-- which may not be sufficient to help
diagnose the cause of error in the system.
Gate set tomography goes beyond randomized benchmarking
by providing process map descriptions of the quantum
gates.
These process maps are operator descriptions
of both the gate and the error seen in the experiment.
Both randomized benchmarking and gate set
tomography require a large amount of data
and are, therefore, limited to the analysis of small quantum
systems.
Developing scalable QCVV techniques
is an ongoing area of research, which
will be increasingly important as larger quantum
systems emerge.
As mentioned earlier, noise and error
is a major concern in today's quantum devices and computers.
One of the main uses of quantum simulation software
is to understand the impact of this noise.
One can apply modeling and simulation
at many different levels of abstraction, ranging
from finite element models of materials to devices
all the way up to quantum circuit models.
QuTiP is a Python-based package that
provides libraries useful for modeling and simulating
open quantum systems, i.e. systems
interacting with unwanted degrees of freedom
in the environment.
Static modeling can also be applied to devices and circuits
to obtain important metrics affecting
their performance as qubits.
These metrics include the coherence time of the qubits
and the sensitivity of the qubit to specific types of noise.
Simulating the performance of quantum error correction
circuits is another important use of modeling and simulation.
Here, one uses simulation to determine the logical error
rate of the circuit and to determine
the scaling of this logical error rate
as a function of the error rate of the individual physical
devices.
One final example of simulation does not involve error at all.
Simulation is also used to understand
the computational advantage that quantum computers have
over classical ones.
Quantum supremacy circuits have been
proposed as circuits that are difficult to simulate
classically but are easy for a quantum computer to execute.
Several groups have developed parallel simulators,
which run on high performance computing systems,
and use these simulators to determine
how large a circuit is required to demonstrate a quantum
advantage.
And so in summary quantum computers
have a software stack that serves the same purpose
as the software stack used for classical computers.
These quantum software tools are important for programming,
design, and testing of today's quantum computers.
And it will be even more important
to the goal of realizing large scale quantum computers.


I think one of the most exciting developments in quantum
computing in recent years has been the ubiquitous access
to real quantum devices.
Just a couple of years ago in a course like this,
students would learn about concepts and quantum
information and quantum computation
without any real means for hands on experimentation.
But in 2016 with the launch of the IBM Q Experience,
the first generation of quantum computers came online.
They've generated a lot of excitement,
with nearly 80,000 unique users running more than three
million experiments.
And this video, I would like to introduce you
to some of the resources that will help you get started
with quantum programming.
Let's start by looking at the composer, which
is a simple graphical user interface for building
and executing quantum programs.
This space has two parts.
In the top part, you see information
about the devices that are available for experiments.
On the left, you see a schematic of the chip
where each white square is one of the qubits.
And right next to that is a diagram of how the qubits
are connected to each other.
This connectivity diagram influences the operations
that you're able to do on this device,
as we'll see in a moment.
One important thing that we have to get
used to when working with quantum computers
is that they're always noisy and imperfect.
So on the right, you see a lot of information
about the level of noise on each of these qubits
and each of the gates.
In fact, you don't have to believe these numbers.
You can design and run certain experiments
that will let you measure the exact errors.
There's a lot more interesting data about each of these chips.
For example, you see that this particular one
is sitting in a dilution refrigerator
with a temperature of around 21 milliKelvin, which is colder
than the surface of Pluto.
At the bottom of the page is the composer itself.
You can see there are five wires, each representing
one of the qubits in our quantum computer.
And on the panel on the right, we
have the gates that are available for building
our quantum circuit.
As you know, the circuit model is a simple, yet powerful model
for quantum computation.
A quantum circuit is basically a recipe
for how to transform the state of a number of qubits
by applying various gates to them.
It can be shown that any quantum computation can
be done by just operating on one or two qubits at a time.
And the very small set of gates is enough for universal quantum
computation.
So as simple as this interface seems,
you can do quite complex computations with it.
So let's do a simple entanglement experiment.
All of the qubits initially start out
as being in the zero state.
To create an entangled pair of qubits,
we first put one of the qubits in a superposition state
by applying a Hadamard gate to it.
Next, we toggle the second qubit conditioned on the first qubit
by applying a CNOT gate.
This leaves the qubits to go in a state of 0, 0 plus 1, 1,
a state that cannot be described in terms of the state of each
qubit individually.
This is an entangled state.
But how can we know what state the qubits are in?
The qubit's state space is inaccessible to us.
And the only way we can get any information
is to measure the qubits.
So let's add two final measurement operations
to this circuit.

But each time we measure the qubits,
we read a normal classical bitstream, such as 0, 0 or 1,
1.
So to be able to infer the state of the qubits right
before the measurement, we have to repeat this experiment
many times and thus approximate the probability
distribution that existed with the entangled states.
So now that we're done building our circuit, let's execute it.
You see that you have the option of either sending
your circuit to a simulator or to real hardware.
First, let's do a simulation to make
sure our circuit is working as expected.
And here is what we get, a histogram
of all the measurement outcomes.
By default in the IBM Q Experience,
each circuit will be executed about 1,000 times.
As we expected, roughly 50% of the time
we measured both qubits in state 0.
And the other 50% of the time, we
measured both qubits in state 1.
This is an indication of the state correlations
that arise as a result of quantum entanglement.
Now let's submit the circuit to a real quantum computer.
By clicking Run, your circuit will
be sent to the IBM Research Labs in New York where
they will be translated to the language
of qubit manipulations, namely control pulses.
After we receive the measurement results,
we see that, indeed, the same outcome is achieved.
However, there are some imperfections here
in the result.
And this is exactly due to the noisy qubits and gates
that I talked about earlier.
The composer is a great tool for just playing around
and visualizing your circuits.
However, you may prefer to build or alter
your circuits more quickly.
You can do this by switching to the QASM
Editor, which gives you a textual representation
of the circuit.
You can also import QASM from file.
QASM, or quantum assembly, is a circuit description language.
In fact, the graphical interface we were using previously
was being translated to QASM code under the hood.
QASM is a hardware agnostic language,
meaning it can be translated to any physical chip or even
a different quantum computing technology altogether.
It expresses data dependencies without explicit timings
for the instructions, which will be decided at a later stage.
Here we see the same circuit we just built written in QASM.
The first line imports a standard library
of gates for us to use.
This is exactly akin to the menu of gates we had previously.
The next two lines define the qubits
in the form of a quantum register of size 5
and the classical bits, which will
be used to hold our final measurement results.
Finally, we have the Hadamard, CNOT,
and measurement operations.
Let's suppose that we want to repeat our entangling
experiment, but this time on two different qubits,
let's say qubit 2 and 3.
This seems trivial.
We just change the indices on Q and C.
However, we get an error message saying that a CNOT is not
allowed from Q2 to Q3.
That's right.
This is due to the connectivity graph of the qubits
in this particular chip.
We see that in order to do a CNOT operation
between these two qubits, we need
to designate Q3 as a control and Q2 as a target.
Luckily, there is an easy transformation that
can be used to flip a CNOT.
This circuit identity is achieved
by sandwiching the CNOT that we have
between two layers of Hadamards, giving us the flipped CNOT.
Now we repeat the experiment on the real chip again.
We see the same result as we expected.
If you look closely, however, you
see that the accuracy of the results
are a little bit degraded compared
to our previous experiment.
This is because our new circuit uses more gates
and this leads to a higher chance of errors accumulating
in the circuit.
To conclude, it's pretty easy to use the IBM Q Experience
to program a quantum computer.
All the many layers of technology
that goes into building a working quantum computing stack
is conveniently abstracted away.
Quantum information science is no longer only done in the lab.
Now you can control a real quantum computer remotely.
While these devices are still small and noisy, in a way,
they force us to be more clever in using them.
For example, we have to take into account the connectivity
of the qubits and try to use fewer gates in order
to preserve information fidelity.
If you visit the IBM Q Experience user guide,
you'll see many more interesting examples of quantum information
science, each one accompanied it with its composer circuit
and QASM code.
And I also encourage you to get involved in the Community
Forum, which is a great place to discuss anything related
to quantum computing and learning from each other.
