
There are numerous examples of quantum mechanical two-level
systems in nature that potentially
could serve as qubits.
For example, the electronic states
of an ion or the electron spin of a phosphorus atom
implanted in silicon or a nuclear spin of a defect
in diamond.
We can even manufacture electrical circuits that
behave as quantum mechanical two-level systems,
or artificial atoms.
But what makes a good qubit?
And how do we assess these qubit modalities
and compare them to one another?
And how can we determine if a particular modality
is well-suited for quantum computing?
We can begin to answer these questions
by first drawing on our intuition
from classical computing.
Basically, same question.
What makes a good classical logic element?
And why did we end up with transistors?
Well, if we want to build a computer at scale large enough
to perform interesting problems, we
should start with a technology that scales well, one
where we know how to define and characterize the logic elements
and where we can manufacture them in large numbers.
These devices must also accurately
represent and process classical information.
We need to be able to set their states to provide
an input to the computer, and we need
to be able to measure the result to get an answer.
Finally, these devices must be robust against failure
in order to complete the computation
and reliably obtain the answer.
Clearly, transistors satisfy all these requirements very well,
and so it's no wonder that computers today
are built from transistors and not,
say, vacuum tubes or mechanical switches.
So with this in mind, what makes a good qubit?
Around the year 2000, Dr. David DiVincenzo, then
a researcher at IBM, articulated five necessary conditions
that any qubit technology must at least possess
if it is to be a suitable physical implementation
for large scale quantum computation.
First, it should be a scalable physical system
with well-defined and characterized qubits.
Second, we must be able to set the input state
and, third, measure the resulting output state.
Fourth, we must be able to perform a universal set of gate
operations.
For example, the single and two-qubit
gates that we discussed last week that are
needed to run an algorithm.
And fifth, the qubits must robustly
represent quantum information.
In many ways, these requirements are
similar to those for classical computers,
and it's only in how the requirements are met that we
can identify differences.
For example, performing a universal set
of one-qubit and two-qubit gates rather than
universal Boolean logic.
Or to robustly represent quantum information,
qubits must have long coherence times,
a concept that loosely translates to the mean time
to failure for a transistor.
In addition to these five requirements
for the qubit technology, David DiVincenzo
also added two conditions related
to the communication of quantum information between qubits.
So continuing from number five, number six
is that the technology must support the interconversion
of quantum information between a stationary qubit and a flying
qubit.
And seven, there must be a way to transfer flying qubits
faithfully between two locations.
Basically, these two requirements
describe a quantum version of an interconnect--
that is, the means to take the quantum information
encoded in one qubit, convert it
to an object that can move, like a photon,
provide the means to guide a photon without loss
to another qubit at a distant location,
and then hand back that quantum information.
Again, analogous to requirements for routing
signals within a classical computer,
but following the rules of quantum mechanics.
These criteria, today referred to as the DiVincenzo Criteria,
articulate the basic requirements
that any qubit technology must possess
if it's to be a viable physical implementation for quantum
computation.


The DiVincenzo criteria articulated the requirements
that a qubit technology must have in order
to be a viable candidate for the physical implementation
of a quantum computer.
In this section, we'll build on two of those criteria, related
to qubit robustness and quantum gates,
in order to define metrics that will
allow us to compare qubit modalities with one another.
To do this, let's first look, in more detail,
at the qubit coherence time, the analog of the mean time
to failure for a transistor.
Quantum computers, like classical computers,
must be built from robust elements.
The coherence time is one metric that
quantifies the robustness of a quantum bit.
Essentially, it's the amount of time,
on average, that a qubit state’s maintained before the quantum
state is lost.
As an illustration, let's consider a qubit
that we set into a quantum state psi,
and consider what happens to that qubit over time.
At first, the state is well-defined,
we just put it in that state, we're
confident that we did a good job,
and so we know what the state is.
Over time, however, the qubit begins
to interact with its environment.
And when it does so, the qubit experiences
noise that alters the qubit state in ways
that we didn't anticipate.
Intuitively, we can imagine that the state begins to blur.
And as time goes on, and the qubit
is subject to more of this environmental noise,
eventually, we can no longer recognize the state,
and the quantum information is fully lost.
Now of course, the qubit is still there,
but it's no longer in the state that we
would have expected it to be in after this amount of time.
The noise has altered the behavior of the qubit,
and it's now in some other state.
Let's now look in more detail at how
we quantify qubit lifetimes, by looking
at errors on the Bloch Sphere.
There are two fundamental ways in which a qubit
loses quantum information.
The first is energy relaxation.
Imagine that we put the qubit in its excited state, state 1.
Unfortunately, it probably won't stay there,
due to noise at the qubit frequency, the qubit will,
at some point, lose its energy to the environment
and return to the ground state.
This loss of energy is called energy relaxation,
and on average, it occurs after a time called t-1.
The second way a qubit can lose quantum information
is through a loss of phase coherence.
Imagine that we intentionally set the qubit at one point
on the equator of the Bloch Sphere.
It likely won't stay in that direction forever,
due to interactions with the environment.
And there are two ways that phase coherence can be lost.
First, the qubit state may move around on the equator,
due to the environmental noise.
If we repeat the experiment many times,
sometimes the noise will drive the Bloch vector east
along the equator, sometimes to the west, and over time,
the Bloch vector fans out more and more.
It does this until, eventually, we
can no longer tell which direction,
or equivalently, which phase, the Bloch vector has.
And the average time it takes for this to happen
is called the pure dephasing time, t-phi.
Now there's another way things can go wrong on the equator.
Remember that, on the equator, the qubit
is in a superposition state of 0 and 1,
with 1 being the excited state.
If that component of the superposition state
loses its energy to the environment,
then the 1 state flips to 0, and the superposition state
is lost.
Essentially, the qubit's relaxed from the equator
to the north pole.
Energy relaxation is also a phase breaking process,
since once the Bloch vector points to the north pole,
we can no longer tell which way it had been pointing
on the equator, that phase information
is lost to the environment.
Thus, the average amount of time that a qubit remains coherent
is related to both the dephasing time, t-phi, and the energy
relaxation time, t-1, which together, give a time t-2,
over which phase coherence is lost.
Thus, a qubit loses its quantum information
by two mechanisms, energy relaxation and loss of phase
coherence, characterized, respectively,
by the times t-1 and t-2.
Now another important metric for quantum computers,
just as with classical computers,
is the clock speed, the time required
to perform a quantum operation.
This is called the gate time, and although it generally
differs for single and two qubit gates,
we can use a typical time, or conservatively,
use the slowest gate time, to define the clock
speed with which we can operate the quantum computer.
And as with all computers, faster is better.
Even if we have an exponential speed
up from a quantum algorithm, it still takes some time
to perform that algorithm, and all else being equal,
a faster clock speed will translate
to obtaining the answer more quickly.
A key figure of merit, then, is the number
of gates one can perform within the qubit lifetime.
The more gates one can implement before an error occurs,
the larger an algorithm one can run.
This metric also illustrates an interesting trade off
with qubits.
In general, qubits with long lifetimes
have less interaction with their environment.
That's good, because they have less sensitivity to noise.
But the trade off is that they also respond more slowly,
even when we intentionally try to control them.
This is because they're not just weakly interacting
with their environment, they're also weakly interacting
with our control fields.
Similarly, qubits that more strongly interact
with their environment may have shorter coherence times,
but they generally also respond faster.
In fact, the number of gates one can perform, on average,
before an error occurs may not differ
much between these two cases.
However, one of these qubit modalities
may have a much faster clock speed than the other one,
and that's a good thing.
This figure of merit, the average number of gates one
can perform before an error occurs,
is a proxy for a more general and rigorous concept, called
gate fidelity, which we'll discuss next.


In the last section, we focused on two
of the DiVincenzo criteria, qubit coherence, and quantum
gates.
We developed an intuitive figure of merit, the average number
of gate operations, that can be performed
before an error occurs.
Such metrics are important, because they
allow us to compare different qubit modalities,
even when those modalities have remarkably different
properties.
However, the definition we introduced only
accounted for errors due to qubit decoherence.
That's fine for qubits that are dominated by decoherence,
but some qubit modalities are limited
by other sources of errors.
For example, control errors, imperfections in the pulses
that are used to drive a gate operation.
For these qubits, even if their coherence times
were practically infinite, their gates
would still be subject to control errors.
So what we need is a more rigorous way
to characterize the robustness of a gate operation, one
that's sensitive to a broad set of error sources.
And that leads us to the subject of this section, a more general
concept, called gate fidelity.
Gate fidelity is a rigorous means
to define how well a gate operation works.
Essentially, it's a measure of how closely our actual gate
operation matches, on average, a theoretically ideal version
of that operation.
For example, if we apply an X gate
to a qubit prepared in state 0, how much do we get to state 1?
Now intuitively, errors could occur along
any direction of the Bloch Sphere
and so we need to check for errors along all directions,
after the operation is complete.
Until this point in the course, we've
only measured the qubit along the Z direction.
But in principle, we can choose to measure the qubit
along any axis that passes through the center of the Bloch
Sphere, including the x-axis or the y-axis.
In addition, gate errors may be manifest differently,
depending on the starting point of the qubit,
so we need to check how the gate performs
against different initial states,
and not just the north pole, for example.
Now at this point, you may be asking yourself,
how is this even feasible?
The qubit state can be anywhere on the surface of the Bloch
Sphere, and that represents an infinite number
of possible initial and final states.
How can we possibly check them all?
Well in fact, we don't have to.
And that's because we can define a basis set that spans
the entire qubit state space.
To draw an analogy, think of global positioning.
Our position anywhere on the globe
can be represented by projecting it onto a convenient basis,
in this case, a coordinate system that spans the globe.
We often use latitude and longitude,
but we could equally well use Cartesian coordinates, x, y,
and z.
Similarly, we can define a basis that
spans the entire qubit state space,
and then use it to specify any qubit state at the input.
We can also use it to characterize any state
at the output, by projecting back onto this basis.
This works, because quantum mechanics
is described by linear algebra.
It's enough to understand projections
to and from the basis set to know what will happen globally.
And in fact, as we'll see later in the course,
such projective measurement plays a crucial role
in the digitization of errors, and our ability
to correct them.
Although the coefficients of a superposition state
will dictate the probability of obtaining a 0 or 1
when measurement is done, for any given measurement,
we will get a 0 or a 1.
In this way, quantum states and their errors,
which appear to be analog, can in fact
be digitized through projective measurement.
Now we saw previously that n qubits can represent 2
to the n states.
Here, the basis can be represented
in a matrix form, and the number of matrix elements
that spans the state space is the square
of the number of states.
So 2 to the n, quantity squared.
For a single qubit, n equals 1, and we need four elements.
For two qubits n equals 2, and the number quickly
increases to 16.
So determining the gate fidelity is essentially
a standard black box type problem.
We have a gate operation, and theoretically, we
know how it should perform.
However, due to errors, its actual operation
isn't precisely known. That's the black box.
And so we need to characterize, on average, how well our gate
operation actually performs.
To do this, we probe the gate operation using the input basis
states, perform the actual gate operation,
and then, for each input, project the resulting output
state onto the entire basis set.
We then compare our results to what
we would expect from a theoretically ideal operation
to determine the gate fidelity.
The approach just described is called process tomography,
and it represents a complete description of the errors
during a gate operation.
It also requires a large number of steps to implement,
as the product of input and output elements
is 2 the 4 n-th power.
Now although there are 2 to the 2 n-th constraints,
due to the properties of these matrices,
this only reduces the total number
of measurements by a small amount, thus, implementing
process tomography scales very poorly
with the number of qubits, and becomes
impractical as n gets large.
This is an issue, because although our gates only
act on one or two qubits, the errors
may cause leakage to other nearby qubits,
qubit 3, qubit 4, qubit 5, et cetera.
And so to account for this, the basis we choose
must encompass all n qubits.
In addition, process tomography is sensitive to all errors,
including initialization errors, when
preparing the input state, and measurement
errors at the output, which although certainly real errors,
are unrelated to the quality of the gate operation itself.
As a result, an alternative approach,
called randomized benchmarking, has also been developed.
Randomized benchmarking essentially
interleaves the gate operation being
characterized with a random assortment of other gate
operations.
Although half of the gates are chosen at random,
we know what they are, and so we can predict the expected output
state, assuming all of the gates were ideal.
This is then compared to the same experiment,
but with only the random assortment of gates,
to see how much the error rate has changed when
adding the interleaved gate.
This change in error rate is then
attributed to the interleave gate itself.
This approach is then repeated for increasing numbers
of pulses, in order to obtain a refined estimate
for the average error per gate, and thereby, the gate fidelity.
Randomized benchmarking is much more efficient
than process tomography, and it's also
insensitive to initialize and measurement errors.
However, it only provides a net error rate,
without revealing specific error channels.
However it's measured, a gate fidelity of 100%
means that our actual operation perfectly
matches the ideal operation.
For example, no matter where our qubit starts on the Bloch
Sphere, our actual x-gate would perfectly
rotate the input state to the correct output state.
Now, as you might expect, it's generally not
possible to achieve a perfect gate fidelity.
There will always be some level of error,
whether due to qubit decoherence during the operation,
imperfections in the control pulse itself, et cetera.
The goal, then, is to see how many
nines, two nines, 99%, three nines, 99.9%, that one
can achieve.
The higher the fidelity, the closer
it comes to an ideal gate.
And as we'll see later in the course, achieving high fidelity
is critical, because it translates directly
to two important aspects of quantum error correction.
First, the fidelity must at least reach a minimum value,
called the threshold, in order for the error correction
to give us a net improvement in the error rate.
And second, once above this threshold,
the higher the fidelity, the less the resource overhead
required to implement the error correction.

Another qubit technology
is based on the internal states of atoms, or neutral atoms,
as they're called, to contrast them with the ions
that we'll discuss next.
Neutral atoms can be trapped by cross-propagating optical beams,
which combine to form an egg carton-like potential.
The qubit states are hyperfine states,
resulting from an interaction between the electron
spin and the nuclear spin.
Such hyperfine transitions are driven
at very well defined microwave frequencies, commonly used
for atomic clocks.
These are highly stable qubits, and as such, their coherence
times are very long.
Thus, the gate fidelity in neutral atoms
is generally limited by control errors.
The main advantage of neutral atoms
is their long coherence times and the ability
to trap these neutral atoms in two-dimensional and even
three-dimensional arrays.
Arrays with up to 1,000 qubits have been demonstrated,
and many hundreds of atoms can be controlled with just a single
laser using an acousto optic modulator.
Another advantage is that the neutral atoms
can be moved around in real time, which
increases the achievable connectivity beyond just nearest
neighbors.
There are a few challenges, however.
One is the large laser power required
to trap and control these neutral atoms.
Another is that loading the trap is a stochastic process.
Atom rearrangement can later be made to fill in the gaps,
but it requires extra steps.
And third, neutral atoms will require integrated optics
to ultimately be scalable, something that's not yet
been implemented, although concepts
exist for its implementation.
The next example, trapped ions, are a leading qubit
modality today.
Trapped ions have been used as atomic clocks for decades,
and these systems are stable and very well characterized.
Ion qubits generally start as atoms,
with two electrons in their outermost shell,
and then one of those electrons is removed through ionization.
The qubit is realized as either an optical transition
between orbital states of this outermost electron
or a microwave transition between hyperfine states.
A primary advantage is that many of the DiVincenzo criteria
are satisfied for trapped ion qubits.
To date, arrays of 30 to 50 trapped ion qubits
have been demonstrated, and surface traps in silicon
are now being developed and used to both capture
and control these ions in a scalable manner.
The primary challenge is the 3D integration of optical
and electrical technologies into the surface traps to make them
scalable.
We'll learn more about trapped ions
and their relative advantages and challenges in the case study
at the end of this week.


The next example, superconducting qubits,
are manufactured artificial atoms.
Unlike the previous examples based on spins
in naturally occurring atoms, superconducting qubits
are electrical circuits that behave like atoms.
Essentially, superconducting qubits
are nonlinear oscillators built from inductors and capacitors.
The inductor is realized by a Josephson junction, a nonlinear
inductor that makes the resonator anharmonic.
As we'll learn in the following case study,
anharmonic oscillators feature an addressable two level system
that we'll call the qubit.
The qubit states can either be states
of phase across the Josephson junction,
flux in a superconducting loop, or even charge on a junction
island.
The main advantages of superconducting qubits
are that the gates are fast compared with the other qubits,
and they're manufactured on silicon wafers
using materials and tools common to CMOS foundries.
To date, arrays of up to 1,000 qubits have been demonstrated
at IBM.
And Google Quantum AI used a 200-qubit array to demonstrate
the scaling of quantum error correction to larger and larger
codes.
The main challenge is the integration
of control and readout technologies
that maintain qubit coherence even
at millikelvin temperatures.
We'll learn more about these challenges, advantages,
and the current state of the art in the following case study.
Finally, there are several other qubit modalities
being pursued that are at various stages of development
and maturity.
The most developed and mature include linear optics
quantum computing, where the presence or absence of a photon
constitutes the qubit.
Quantum information is processed using linear optical components
like beam splitters, phase shifters, mirrors,
and interferometers.
Effective nonlinear interactions are
achieved through the use of single photon sources,
photodetectors, and the like.
The main challenge with linear optical quantum computing
is that it's very hard to make photons interact with one
another.
In addition, high fidelity memory is a big challenge,
and many schemes rely on probabilistic sources and gates
to process information.
Another type of quantum computer based on neutral atoms
is a quantum emulator.
A quantum emulator uses Rydberg atoms,
or Bose-Einstein condensates to emulate a condensed matter
or atomic system through the use of tailored atomic energies
and coupling terms.
A more exotic qubit modality that
is generating significant interest today
is based on something called a Majorana fermion, a fermion
that is its own antiparticle.
Several efforts worldwide are trying
to realize a Majorana qubit, using a combination
of superconducting and semiconducting
materials, which feature a strong spin orbit interaction.
If successfully realized, Majorana qubits
have been theoretically shown to exhibit topological protection,
a resilience to noise that's not unlike the resilience afforded
by quantum error correction.
The challenge is that they're extremely difficult to realize,
and to date, there's been no definitive demonstration
of a Majorana qubit featuring this topological protection.
Other qubit candidates include molecular ions,
which are trapped and controlled in a manner
similar to atomic ions, and electrons
on liquid helium, which are basically free electrons that
form an electron lattice on the surface of liquid helium
and can be controlled using electron spin resonance
techniques.

In this section, we'll
compare the different qubit modalities
that we just discussed.
We'll first do this in the context of the DiVincenzo
criteria and then compare the gate fidelity and the clock
rate for single-qubit and two-qubit gates.
Let's begin with a stoplight chart and the DiVincenzo
criteria.
Now, this is certainly going to be a subjective assessment.
And with all of the ongoing rapid technology development,
the actual coloring will certainly change over time.
Still, it's useful to take a snapshot of the current state
of the art to gain insight into the relative strengths
and challenges that different modalities face.
And that's our purpose here.
Our stoplight chart assigns colors to indicate progress.
Green will indicate that a modality has made the requisite
demonstrations and has sufficiently matured
to the point that we can envision it proceeding
to 100-plus qubits.
Yellow indicates that concepts or first demonstrations may
exist but that the technology is not quite ready to scale
to the 100-qubit level.
Red indicates that no realistic concepts are currently
known that would enable reaching 100 qubits.
However, we're not going to consider
any of these qubit modalities, as they're still too
nascent for our purposes here.
So you won't be seeing any red.
Starting with the first DiVincenzo criteria, D1,
scalable systems, the most mature or neutral atoms,
trapped ions, and superconducting qubits all have
demonstrated systems of 10 to tens of qubits,
with 50-qubit prototypes coming online in the near future.
Silicon, germanium, and doped silicon qubits
are yellow because they'll require high wire
counts to address their qubits, and those wires
need to be routed with high density due to the relatively
small qubit geometries.
All of these issues will need to be addressed with 3D
integration, which is only just beginning to be conceived
for these modalities.
In addition, both doped silicon and NV centers are currently
limited by the inability to implant high coherence dopants
or defects with the precision required to reach the 100-qubit
level.
Next, for initialization, D2, most technologies
are doing pretty well.
The one exception is NV centers, where
the strong laser used to initialize the qubit
will occasionally remove an electron.
This makes the defect charge neutral, effectively destroying
the qubit until it's reset.
For measurement, D3, the measurement of neutral atoms
is extremely slow and would certainly
limit the ultimate clock speed of an error-corrected system.
That's why this one is colored yellow.
In terms of D4, universal gates, the doped silicon community
has not yet reported a two-qubit gate fidelity.
For neutral atoms and silicon germanium qubits,
although their two-qubit gates have been demonstrated,
they still have a relatively low fidelity, around 80%
And that's why these are colored yellow.
In terms of coherence, D5, all of these technologies, in fact,
grade fairly well.
For D6 and D7, the interconversion
and communication of quantum information,
there's been no published work yet for silicon, germanium,
or doped silicon approaches, although it's
anticipated that a conversion to microwave photons
should follow from the same approach
as used for superconducting qubits.
Now, as we can see, both trapped ions and superconducting qubits
have made significant progress toward meeting the DiVincenzo
criteria.
This is one reason they are viewed today
as leading candidates.
Let's turn now to the gate fidelity and gate
speed of these modalities.
The number of operations before an error occurs
is directly related to the fidelity,
and they're plotted here against the gate speed
for single and two-qubit gates.
The upper right corner represents the best performance.
Additionally, it's desirable to be above the dashed red line,
which is representative of the most lenient threshold
for quantum error correction.
What we see is that trapped ions have the highest
single-qubit fidelity.
On the other hand, they are about 500 times slower
than a superconducting qubit gate.
For two-qubit gates, superconducting qubits
and trapped ions have similar levels of gate fidelity,
but again, the superconducting qubit gate is about 1,000 times
faster than the ion traps.
Some technologies, like doped silicon,
have measured and reported single-qubit gate fidelities,
but they're still working on their two-qubit gate fidelities.
Again, we can see that both trapped ions and superconducting
qubits are leading modalities today.
And in the case studies, we'll take a detailed look
at each of these technologies.

In this case study, we'll
take a 360 look at the trapped ion qubit modality.
Trapped ions were the first qubit technology,
and this is primarily due to their historical use
in atomic clocks and precision measurements.
Ions start as neutral atoms, the chemical elements
in the periodic table.
For example, we'll hear about strontium in this case study.
A strontium ion is formed when its outermost
electron is removed, a process called ionization.
With one less electron, the atom now has a net-positive charge,
so it's no longer charge neutral,
and we'll call this an ion.
Because the ion's charged, it can be trapped or held
in place using oscillatory electromagnetic fields.
Although these fields used to be applied
using large electrodes arranged in a three-dimensional
configuration, today they're implemented
using surface traps, electrodes manufactured
on silicon wafers that hold the ions just above the wafer
surface.
Trapped ion qubits are one of the leading modalities being
developed to realize a quantum computer,
and it has a number of advantages.
From a business perspective, trapped ions
are attractive because they leverage
a substantial existing technology
base, one that goes back three decades
to the development of atomic clocks and mass spectrometers.
In addition, trapped ions today are fundamentally
a silicon-based technology.
The surface traps themselves are fabricated on silicon wafers,
and they use standard semiconductor fabrication tools
and techniques.
In addition, all of the key control and readout circuitry
can be integrated with existing CMOS electronics.
For example, the electrode voltages
used to hold and move the ions or the integrated photonic
waveguides and gratings used to optically control the ions
and even the photodetectors used to read out the ions
are all compatible with existing CMOS foundries and materials.
And in this sense, they're lithographically
scalable to large numbers of qubits.
Today, there are a growing number
of commercial efforts pursuing and supporting
the development of trapped ion qubits,
including companies like IonQ, Quantinuum, Alpine Quantum
Technologies, and Oxford Ionics.
From an engineering perspective, the surface traps
used to capture and hold ions are
designed using standard CAD software and layout tools.
The electrode control electronics are CMOS circuits,
and they're designed in the same way as conventional CMOS
electronics.
Similarly, the photonic waveguides and couplers
are designed and integrated directly into the silicon.
Scientifically, state of the art trapped ion quantum processors
have demonstrated several prototype quantum algorithms,
such as Shor's algorithm at the 10 qubit level,
and larger scale circuits at the several tens of qubits level
have been used to encode logical qubits
and even perform certain logical operations.
Although trapped ions operate more slowly than superconducting
qubits, they've demonstrated a larger degree of connectivity
between the ions, and this may help
to offset the relatively slow speed by making problem
embedding more efficient.
And finally, from a technology standpoint, trapped ion qubits
leverage both microwave and data communications technology.
The lasers used in trapped ion experiments
have application to atomic clocks, precision navigation,
even biology and optogenetics.
Developing compact instrumentation,
for example, size, weight, power, even cost,
will benefit an array of technologies,
even beyond trapped ions.
And so, with that brief introduction,
let's now hear from the experts, who
will present a 360 view of trapped ion qubits.


We use individual charged atoms, or atomic ions,
as quantum information carriers in our development
of a large-scale quantum information processor.
Starting with neutral atoms with two electrons
in the outermost level, we can remove one of these electrons,
producing an ion with a positive charge
that we can hold onto very tightly using
electromagnetic fields.
In machines like these, we can trap
individual atoms, the smallest amount of an element--
in our case, strontium or things like calcium--
that you can.
That's one atom.
That's something like smaller than a tenth of a nanometer.
And we manipulate them with lasers
and electromagnetic fields such that we
can hold onto them for many hours
and manipulate their quantum states to do things
like quantum information processing.
So in an individual trapped ion, the amount of time
that the quantumness survives, or the coherence time,
can be made to be very long.
In systems like this, where people manipulate trapped ions
on a regular basis, this coherence time
can be seconds, even minutes.
And this allows us to do lots of coherent quantum operations
between larger numbers of qubits in the amount of time
that you have available to do anything with those quantum
systems.
Other advantages are that the error rates in the quantum
operations that we perform--
single qubit, double qubit operations
that are keys to quantum information processing, as well
as preparation and readout of the quantum states--
can be done with very low error rate in trapped ion systems.
Because these atomic systems are very clean, single quantum
systems that we can control very well,
we can theoretically predict exactly how
they're going to behave.
We know where they are, and we can manipulate their states
very, very cleanly.
We've now defined our qubit state within a single ion,
but how do we hold on to one atom?
Utilizing the positive charge of the ion,
we can trap it in a combination of static and dynamic electric
fields.
By applying a radio frequency electric field
to two diametrically opposed rods out
of a four-rod square configuration,
we can produce a quadripolar field in two dimensions.
At any one moment in time, this field
will tend to push an ion toward the center of the trap in one
dimension and push it away in the other.
But since this field oscillates in time,
for the right combination of frequency and amplitude,
the ion can effectively be pushed
toward the center in all directions
as if it were in a two-dimensional bowl.
In the third dimension, we can apply
a combination of static voltages to trap the ion.
This is the same technology used for mass spectrometry,
and we see potential offshoots of ion quantum information
processing in improvement to small sample
sensing and identification.
A promising approach to large-scale ion control
and manipulation is based on chip-based traps,
as shown here.
By patterning metal using standard microfabrication
techniques onto an insulating substrate,
we can produce a flat version of the four-rod trap
structure I just described.
As we'll describe in a bit, ions are trapped in space
above the center of the trap where the quadripolar trapping
field is produced.
To hold onto an individual ion for a long time,
a very low pressure environment is
required, as molecules in the air
have sufficient energy to knock the ions out of the trap.
Ultra high vacuum conditions with background pressures
more than 12 orders of magnitude less
than standard atmospheric pressure
can be maintained in specialized chambers.
These extremely low pressures are produced in our laboratory
by means of cryopumping, in which various surfaces
in the chamber are made very cold,
within a few degrees of absolute zero,
by means of refrigeration.
Much as water condenses from the air
onto a cold beverage container on a humid day,
cryopumping results in condensation of almost all
of air's constituents, quickly and dramatically
lowering the pressure in the closed vacuum chamber.
Ions can be maintained for hours to days in UHV systems
like this.
It is important to point out that the ions themselves
are not cooled in this manner.
They're cooled to much lower temperatures,
eventually to only a few tens of millionths of a degree
above absolute zero, by the use of lasers.
Perhaps counterintuitively, it is
possible to remove motional energy from atoms
by allowing them to absorb light at a very particular frequency,
after which they re-emit light at a slightly
higher frequency, leading to a reduction in motional energy.
This laser cooling process, developed 30 years ago,
is a key enabling technology for quantum computing
with atomic systems.
This animation shows the process by which we get individual ions
into the trap.
Inside the vacuum system, we heat up
a piece of metal to a few hundred degrees Celsius,
producing hot atomic vapor.
Using a combination of laser beams and a magnetic field
gradient, we cool approximately a million neutral atoms
into what is known as a magneto-optical trap.
These cold atoms can then be accelerated toward the ion trap
chip using another laser beam.
With the radio frequency trapping potential applied
to the trap electrodes, neutral atoms that are ionized,
using other lasers within the trapping volume,
will feel the trapping fields and be
localized within the trap, where they are cooled
with yet another set of lasers, these ones
resonant with transitions in the ion.
The result is a single atom held in space
approximately 50 micrometers from the surface of the chip.
We can image the ions using the light
they scatter during cooling, producing images
like that shown here.


Once we have the ions, how do we manipulate the qubits?
Single-qubit gates are brought about
by applying laser pulses resonant
with the qubit transition for a certain amount of time.
If the qubit starts in the ground state
as a function of the laser pulse duration,
the qubit state coherently oscillates between the ground
state and the excited state, performing what
are known as Rabi oscillations.
By choosing the appropriate time to stop the Rabi oscillations,
we could perform a flip of the quantum state
from 0 to 1 producing a quantum version of the classical NOT
gate, or the inverter.
This is how we perform a pi pulse.
Interestingly, if we use a laser pulse
half as long as a pi pulse to perform a pi over 2 pulse, that
is a gate with no classical analog,
we produce in the ion qubit a superposition state,
0 and 1 at the same time, where the electron is effectively
in two states at once.
These manipulations form the basis
of single-qubit operations on ion qubits.
Along with single-qubit gates, 2-qubit gates
are required to do arbitrary quantum computations.
We bring about these operations by means of the strong Coulomb
interaction between two positively-charged ions.
Two ions in the same trap share vibrational modes
due to their interaction, much like two balls with a spring
connecting them.
And these modes can be excited, depending
on their internal qubit states, using laser beams.
Thus the internal qubit states can
be entangled through the quantum vibrational mode
channel used as a quantum bus.
The basic 2-qubit gate is a controlled NOT gate,
somewhat analogous to a classical exclusive OR gate.
And it can be produced using this bus interaction
in combination with a few single-qubit gates,
as I just described.
If one ion starts in an equal superposition state,
the state after application of a controlled NOT gate
will be a maximally entangled state,
capable of effects like what Einstein called
"spooky action at a distance.”
Not only is this spooky action really
the way entangled systems work, as verified many times
in laboratories around the world,
it is also a fundamental component
that large-scale quantum computers will rely on
for their operation.
Finally, after a series of single and 2-qubit operations
as you would perform to carry out an algorithm,
the quantum state of the ion qubit must be measured.
Ions allow a particularly good mechanism
for high-fidelity state readout, when
compared with other systems.
By illuminating the ion with light resonant
with an auxiliary transition, we cause
the ion to absorb and re-emit light on this transition
if it is measured in one state, whereas the light will
be off-resonant if it is measured to be in the zero state,
and the ion will be dark.
The ion state may have been in a superposition
before the measurement, but during illumination, the state
will be projected to 0 or 1 and remain there.
This forms a quantum non-demolition measurement,
allowing us to scatter many photons
and get good statistics on the ion state.
By setting a threshold on the number of photons
we detect from the ion during measurement
using a single photon-sensitive detector,
we can measure the ion's state with very high fidelity.
We therefore have established techniques
to perform all the operations required for quantum computing
using trapped ions, and the properties
of the ions themselves allow for very
low error on these operations.
In fact, researchers in the field of trapped ion quantum
computing have demonstrated basic quantum computing
primitives in few ion experiments that
approach or surpass the fidelity levels we think we need
for useful large-scale systems.
Coherence times for a single ion have
been shown to be in the neighborhood of 10
minutes, quite a long time for quantum properties
to persist, even becoming comparable to human time
scales.
Single-qubit gates, with errors at the one in a million level,
have been achieved using microwave fields.
And 2-qubit gate fidelities are at the 99.9 percent level
in experiments performed by a few different groups.
In addition, a few tens of ions have
been trapped and individually manipulated as well, though not
simultaneously with the highest fidelity gates.
The remaining challenge, therefore,
is to maintain the exquisite level of quantum control
that has been shown to be possible,
while scaling systems to many ions.
This must include providing control and readout capability
for arrays of ions without simply multiplying up
the number and size of the bulk optics
and external electronics setups used today--
equipment which can take up a small room.
This is an exciting area of current research.
And at Lincoln Laboratory and MIT,
we are taking this challenge head on.


As you heard previously, all the required operations
for performing quantum computing with trapped ions
have been demonstrated in research groups
around the world.
However, this has been achieved in only few-qubit systems,
that is, with around 1 to 10 ions.
Perhaps the most significant obstacle
to realizing a practically useful quantum computer
is the current lack of ability to control and measure
very large numbers of ions.
And we think we'll need thousands to millions,
with the same exquisite precision demonstrated
in the few-ion systems.
This is the direction, the direction
of so-called scalability, in which the field is looking,
and in which our group at Lincoln Laboratory
is playing a leading role.
Really, there are four key things
we need to do with our trapped ion qubits.
I'd like to go through them and discuss the technology being
developed to address how we might
do each one on a large scale.
That is, on a large number of ion qubits.
First, ions need to be trapped, or held in fixed positions.
You already heard that this is done
with a combination of voltages, both static and oscillating,
that are applied to metal electrodes placed around
the positions we'd like the ions to be trapped in.
These electrodes are typically centimeter to millimeter scale,
and are made in standard machine shops.
This works well for few-ion systems, but to trap
very large arrays of ions finely detailed
and complex electrode structures are required.
And this is something very difficult to achieve
with machining techniques.
What you'd really like to utilize
are micro- or nanofabrication techniques,
like those employed for making classical computer chips,
where metal layers are deposited on wafer substrates,
like silicon or sapphire, and are subsequently
finely patterned using what is called optical lithography.
Fortunately, we've figured out a way
to use these techniques to make ion traps.
It turns out it works to unfold the electrodes normally placed
around the ion onto a plane that lies below it.
By applying a similar set of voltages
to these planar electrodes, the ion
can be trapped above the surface of the plane,
with the surface to ion distance scale being set by the size
and spacing of the electrodes.
Since these planar electrodes can
be fabricated using microchip techniques,
they can be made small, and in an arbitrary pattern.
This allows us to produce large numbers
of zones arrayed in two dimensions for large numbers
of ions to be trapped in, as well
as to reduce the size of the electrodes
to the micrometer scale.
In these types of traps, which we call surface electrode
traps, ions are typically trapped a few tens
to 100 microns above the chip surface.
An important additional benefit of these microchip
surface electrode traps is that they provide
a platform for integration of a host of other key ion control
technologies.
We basically have the potential to put anything
we can currently put in classical computer chips
and more into these ion traps.
The second key thing we need to do with our ions
is control their internal quantum states.
That is, perform the actual quantum gates or quantum
operations.
Here, I'm including the initialization steps
of cooling the motion of the ions,
as well as setting the internal electronic states in which
the ions begin a computation.
As you already heard, this is done primarily with lasers.
For the types of ions we plan to use,
we require about a dozen different laser wavelengths,
ranging from the near ultraviolet
to the near infrared, pretty much over
the whole visible spectrum.
These layers are directed and tightly
focused on the ions, which are housed inside a vacuum chamber,
through the chamber windows using
large numbers of bulk optics, like mirrors and lenses.
This is a pretty effective way to control a few ions,
but it is nearly impossible to imagine
how to use bulk optics to address a large ion array.
We need to find a way to focus a dozen different colored laser
beams on each ion in a highly controlled manner.
For example, we will want the ability
to hit one ion that resides, say,
in the middle of a large two-dimensional ion
array with one particular laser beam without hitting any
of the other ions, which would lead to some kind of operation
error.
A dream would be to plug a fiber for each color of light
we need into the chip, and have that light routed
around the chip, much like a metal trace or wire routes
electrical signals.
This light will be split up into many paths of the chip,
and then directed and focused out of the chip plane
to each ion location.
Perhaps surprisingly, this technology actually exists.
It's called integrated photonics,
and we are beginning to incorporate it into ion traps.
You can think of integrated photonics as basically fiber
optics on a chip.
These tiny fibers called waveguides
are made by depositing the right materials, which of course have
to be transparent over the visible spectrum,
onto the trap chips.
These materials are then patterned
using the same techniques used to pattern
the ion trap electrodes.
These waveguide patterns define the paths
that the laser light travels along,
and we can design them to split the light from one path
into many branches.
To get the light out of the chip and onto the ions,
we can pattern periodic gaps in the waveguide material that
act like a diffractive grating.
This grating will bounce and focus the light
into the vertical direction.
This out-coupling process works in reverse.
And it turns out to be a very effective way
of getting the light into the chip from, say,
a fiber optic cable coupled to the laser source.
At Lincoln Laboratory, in collaboration with MIT,
we've demonstrated quantum control of trapped ions
with light integrated into a surface electrode ion trap
chip.
In this case, the waveguides run below the trap's metal
electrodes, and we pattern holes in the electrodes
so that the light can get through to reach the ions.


The third thing we need to do with our ions
is to measure or read out their quantum states.
As explained earlier, this is done
by counting photons that are emitted from the ions
when they are illuminated by a readout laser.
This readout needs to be done fast,
and the speed is determined by the number of photons
you can collect from the ion, and how quickly and efficiently
the photon detector can give you a click when
the photon hits it.
Ions emit light isotropically, or in all directions,
so it's not very easy to collect it all.
For few-ion systems, light collection
is typically done with a very large lens,
which, due to its size, is located outside the vacuum
chamber.
This can collect a few percent of the total emitted light
and send it to a detector, such as a photomultiplier tube that
converts individual arriving photons
into short electrical pulses that we
can count with electronics.
This works well because you only have
to collect from a very small region in space
where the few ions reside.
For large arrays of ions, this technique
is highly inefficient.
Instead, we are now working to eliminate the large collection
lens and integrate the photon detectors into the ion trap
chips with a detector right below each ion.
Since the detector is located only a few tens of micrometers
away from the ion, they can be made very small
and still collect the same amount of light
as a big lens placed far away.
At the same time, these detectors
can be arrayed around the ion trap chip in very large numbers
to match the size and pitch of the ion qubit array.
This can, in principle, be a very efficient and scalable way
to collect and detect light in a trapped ion quantum processor.
The detectors that we are using for this purpose
are known as Avalanche Photodiodes, or APDs.
They are routinely fabricated by academic research groups
and by industry using the same facilities and techniques that
are utilized for microchip technology.
And there is therefore a clear path to incorporating them
in our ion traps.
Indeed, at Lincoln Laboratory and MIT,
we've already demonstrated that we
can detect photons emitted from trapped ions
using these integrated APDs.
The fourth thing we need to do with our ions
is move them around.
We call this shuttling, and it provides
a capability that is quite unique to the ion qubit
modality.
You have to find some way to move and distribute
quantum information around your quantum computer in order
to create the large entangled states required
for practical quantum algorithms.
Ions can be shuttled by changing the voltages applied
to the trap electrodes.
The voltages are typically generated
with electronics located outside the vacuum system,
and brought to the electronics via long wires
that are connected to the chip around the edges.
This is done routinely, and is fairly
straightforward for few-ion systems,
because there aren't that many electrodes
and corresponding voltage sources required
for such a small scale.
However, for large arrays of ions,
we will require lots of electrodes,
and therefore lots of voltages and wires.
Think about 10 per ion.
Once again, we lean on integration
to solve this scalability problem.
At Lincoln Laboratory, we've begun
to develop tunable voltage sources that
are integrated into ion traps, with an individual voltage
source below each electrode and connected
through on-chip wiring.
We can use commercial CMOS foundry facilities
to fabricate these integrated electronic devices because they
are built from the same transistor technology that
is used in classical computer chips.
These individual voltage sources, called Digital
to Analog Converters, or DACs, can all
be programmed and varied at high speed
with digital signals that come down just a few wires
connected to the trap chip, similar to
the USB communication protocol.
I'd also like to point out that, as we go forward,
there are other electronic devices that we can think
about integrating, things like circuits that
detect the electrical pulses from our photon counters,
or even classical computing processors that
can store and manipulate classical information.
As you might expect, we ultimately
need to integrate these different control
and measurement technologies together into one chip.
This means that we need to use a fabrication process that
is compatible with it all.
This is not a trivial concern, since the performance
of the required devices is very sensitive to the fabrication
techniques and to the particular materials used.
We keep this important constraint in mind
as we develop our scalable technology,
and make sure we are keeping everything compatible.
In particular, all of the technologies I've discussed
are completely compatible with advanced CMOS fabrication
techniques and materials.
This means that we are truly poised
to take advantage of all of the incredible scalable
technology that has been developed
for classical computers, propelled by billions
of dollars of investment over decades for our quantum
computer.
This animation is our vision of what a scalable trapped ion
quantum computer will look like.
Ions are trapped above the plane of a surface electrode ion trap
chip.
They're individually addressed and controlled
with laser light delivered by integrated photonics,
and light emitted by the ions is detected
with integrated single-photon APDs below the trap electrodes.
The ions are shuttled around by varying the voltages
on these trap electrodes using integrated electronic circuits.
The movie shows a particular quantum computing algorithm,
and you may think to yourself, this
doesn't look like a computer.
To that I would say that we are trying
to build something that computes in a fundamentally
different and transformative way.
And with this in mind, I would argue
that we shouldn't expect it to look
like anything we've ever seen.


In this case study, we'll
take a closer look at superconducting qubits.
Superconducting qubits are electrical circuits
built from inductors, capacitors, and Josephson tunnel
junctions that, when cooled to millikelvin temperatures,
exhibit quantum mechanical behavior.
In fact, it's often said that superconducting qubits
are artificial atoms.
And what's meant by that is that these circuits can
be designed to have properties similar to atoms.
For example, the energy level separation
between state 0 and state 1, or their sensitivity
to environmental noise, can all be determined by design.
And this is quite different than qubits based on elements
that we find in the periodic table,
where you basically have to go with what nature provides.
Today, superconducting qubits are
one of the leading modalities being developed
to realize a quantum computer, and there
are a number of advantages.
From a business perspective, superconducting qubits
are attractive because they leverage a substantial existing
technology base.
For example, superconducting qubits
are fundamentally a silicon technology.
They're fabricated on silicon wafers.
They use standard semiconductor fabrication tools
and techniques.
And the materials, like aluminum or titanium nitride,
are fully compatible with CMOS foundries.
In this sense, they're lithographically
scalable to large numbers of qubits.
From an engineering perspective, superconducting qubits
are designed in much the same way
as classical transistor-based circuits.
They use the same kinds of CAD software
for layout and simulation, and have
many of the same considerations as larger scale computer chips.
For example, when routing wires to and from the devices.
Scientifically, state of the art superconducting quantum
processors are pushing 1,000 qubits,
and this is at a level where even the largest foreseeable
classical computers, let alone the ones we have today,
simply would not be able to simulate that quantum computers
behavior or its output.
When this happens, we'll have reached
a point that's often referred to as quantum supremacy,
a point where a quantum computer has performed
a task that could not be calculated exactly
on a classical computer.
And finally, from a technology standpoint,
superconducting qubits leverage and rely
on existing technologies, such as microwave control electronics
and microwave packaging, often using the same frequency bands
used in cell phone electronics.
And so, with that brief introduction,
let's now hear from the experts, who'll
present a 360 view of superconducting qubits.


Superconducting circuits are a quantum computing modality
where quantum information is stored in superpositions
of charge and current.
In a superconducting metal, as you cool it down
below some transition temperature,
the electrons pair up into what's known as Cooper pairs
after one of the inventors of the most
successful theory of superconductivity,
the BCS theory.
The B is for Bardeen and the S is for Schrieffer.
Superconductors have many applications.
And there's a large market for them
far beyond for quantum computing.
Superconductors have zero resistance at DC frequencies.
So they're really useful for applications
where you have large currents, for example, to create
large magnetic fields.
So if you get an MRI, the large magnetic fields
are probably generated by currents going around
in superconductors.
If you tried to make those fields out of regular wire,
you'd have so much heating that it wouldn't work.
Superconductors are also sometimes used
for maglev trains and for low power
classical digital circuits.
One of the most simple types of superconducting circuit
is just a linear harmonic oscillator made up
of some inductor, L, and a capacitor,
C. In an LC oscillator, if you put in energy
at the right frequency, it will cycle
between charging up the capacitor
and putting current through the inductor.
How fast this happens depends on the values of the capacitor
and the inductor.
But for the circuits we're talking about,
it happens a few billion times a second
or at gigahertz frequencies.
This is also the same frequency that a lot of consumer
electronics work at, like your Wi-Fi network at home
or your cell phone, which means that we
get to use a lot of equipment that's been developed
over the years to meet growing consumer and commercial needs.
A linear harmonic oscillator has equally spaced energy levels.
And the energy spectra is quantized,
meaning you can only have a discrete number of excitations.
You can observe this quantization
provided your circuit is cold enough
that the energy associated with the temperature
is much less than the energy level spacing
and provided your materials are good enough
that you don't lose much energy every oscillation period.
This is one of the reasons we need to use superconductors.
If the metal were normal, we'd lose too much energy
per oscillation period.
However, there's a problem with using
a simple linear oscillator as a qubit.
If you have a qubit, you want to be
able to move it around the Bloch Sphere
into superpositions of 0 and 1.
But in a linear oscillator, all the energy levels
are equally spaced.
This means that if you're in the 1 state
and you try to put in energy to make the qubit go to the 0
state, you can end up in the 2 state or some higher state
instead.
And so we can't think of our system as a qubit
anymore, because a qubit should only have two energy levels.
The way to make a linear oscillator into something
that can be used as a qubit is to introduce
a non-linear element.
That will make it so the energy splitting between the 0
and the 1 state is different than the energy levels
between the other states.
The most common way of doing this
is to use a Josephson junction, or JJ.
JJs were predicted by Brian Josephson in 1962.
A JJ is just a very thin insulating barrier
between two superconductors.
If the barrier is thin enough, the superconducting electrons
can tunnel through the barrier without losing any energy.
The most important thing about a Josephson junction
for our purposes is that the inductance
depends on the current going through the junction.
This is different from a loop of wire
where the inductance is just a fixed value.
And the nonlinear dependence of the inductance
changes the energy spectra, so the levels
are no longer equally spaced.
This means we can uniquely address
one energy level, which we're going to make into our qubit.
One of the DiVincenzo Criteria is
that we have to be able to initialize our system.
If we want to be able to put our system in the ground state
and have it stay there, it's important
that thermal excitations don't excite the qubit out
of the ground state.
That means we need to be cold.
Exactly how cold this is depends on what the energy levels are.
A typical superconducting qubit frequency of 5 gigahertz
corresponds to about 250 milliKelvin.
So we need to be much colder than that,
around 10 milliKelvin or so.
You can get to these temperatures
using dilution fridges.
This is a three-case stage, 3 Kelvin, so 3 degrees
above absolute zero.
We get to that temperature by using a pulse tube
cooler, which you might be able to hear in the background.
And then to get colder, we use a dilution refrigerator,
which actually uses a mixture of helium-3 and helium-4.
Helium-3 is just a lighter isotope of helium-4.
And the basic concept behind a dilution refrigerator
is that it's similar to the way you cool a cup of coffee.
You blow across the top of it.
And what you're really doing is removing the vapor.
And what has to happen is more coffee has
to come out of the liquid and into the vapor,
and that takes energy, and that's how your coffee cools.
So we can use the same trick with helium-3 and helium-4.
Dilution fridges used to be very specialized, hard to use,
and required liquid helium.
Now, in part driven by the interest in quantum computing,
companies are making automated systems that are much easier
to operate and to maintain.
They also don't require a continuous source
of liquid helium to run, only electricity.


One of the neat things about superconducting qubits
is that they are macroscopic things,
but they act a lot like atoms.
They have discrete energy levels and you
can couple them to cavities just like you can with atoms.
With atoms you have cavity quantum electrodynamics,
or cavity QED, that describes how light in a cavity
interacts with atoms.
And with superconducting qubits you
have circuit QED, which describes how light in a cavity
interacts with superconducting circuits.
The math is basically the same.
But unlike with atoms where you're
limited to whatever's on the periodic table,
with superconducting qubits you can engineer the energy levels
to be whatever you want by changing
the values of the capacitors and the sizes and numbers
of the Josephson Junctions.
This is why superconducting circuits are sometimes
called artificial atoms.
Because they're like atoms but you
can engineer their energy levels.
Here's a picture of a fabricated superconducting qubit.
The two squares of metal make up the capacitor.
In between them is a loop of superconducting material
that has JJs in it.
In this type of qubit it's easiest to think
of the information being encoded in currents moving
clockwise and counterclockwise.
To control the qubit we can send in a pulse of microwave energy
at the qubit's frequency.
The phase and length of the control pulse
will determine how much the qubit rotates around the x
and y-axes of the block sphere.
So this instrument is called an arbitrary waveform generator.
And this you can think of as essentially the central command
for the experiments.
So these are what we're going to load
our qubit pulses, our entangling pulses, and our readout pulses
in.
So it's going to send, for example, your INQ signals
to your qubit.
It could also send an and INQ signal to your readouts.
So this would be sufficient to control
at minimum, a single qubit.
By multiplexing, that is by sending signals
at multiple frequencies down the same lines,
we can actually use a unit like this
to control multiple qubits at the same time.
Typical single qubit control pulses
are tens of nanoseconds, which is very short compared
to the best coherence times of 100 microseconds
and fidelities greater than 99.9% have been achieved.
Now, we also need to be able to do two qubit gates between two
superconducting qubits.
There are lots of ways to couple of superconducting qubits
to each other, including coupling them directly
to each other through a capacitive, or inductive
interaction, or mediating the coupling with a resonator
or another qubit.
In many coupling schemes, it's necessary to change the energy
levels of the qubits, which we can
do by changing the magnetic flux through the loop.
To qubit gate times range from tens
to hundreds of nanoseconds.
And gate fidelities greater than 99% have been demonstrated.
Now, at some point in our quantum algorithm
we also need to be able to get information out of the qubit.
One common way of doing this is to couple it
to a linear resonator, like the harmonic oscillator
we talked about before.
In this picture, we see a qubit coupled to a readout resonator.
Previously, we talked about using
an inductor and a capacitor to make a resonator.
But in this case, we're just taking a microwave transmission
line that has a distributed inductance and capacitance
and is also a resonator.
The qubit interacts with a resonator
just like an atom interacts with a cavity.
And we end up shifting the resonator frequency
by a different amount if the qubit is in the zero
state or the one state.
So by sending a pulse of microwave energy
to interrogate the resonator, we can
learn the state of the qubit.
Readout times vary but can be as short
as hundreds of nanoseconds.


We often say that superconducting qubits
are artificial atoms.
What we mean by that is that we can build electrical circuits
that behave much like the natural atoms
on the periodic table.
For these artificial atoms, we can
design all of their properties-- their energy level
spacing, their sensitivity to noise, and so on.
This is quite different than qubits based on natural atoms,
where we're limited to what we're given by nature.
And so a key advantage of superconducting qubits
is that we design these superconducting quantum
circuits and their properties.
A second advantage is that superconducting qubits
are a silicon technology.
We manufacture superconducting qubits
on silicon wafers using the same tools--
photolithography, metal deposition, metal etch--
that are used by industry to make
Complementary Metal-Oxide-Semiconductor,
or CMOS, transistors.
The active elements we use, Josephson Junctions,
have thin oxide barriers, just like the thin gates
of transistors.
Even the metals we use-- aluminum, titanium nitride,
niobium--
are all compatible with CMOS fabrication.
And so in a very real sense, superconducting qubits
are a silicon technology.
And this affords us lithographic scalability.
It's a straightforward path to increasingly complex circuitry
with many interconnected qubits.
There are a few differences related to the specific process
temperatures and other processing parameters that
are used for CMOS and for superconducting qubits.
And this is related primarily to the need for pristine materials
and fabrication in order to maintain high qubit coherence.
Superconducting qubits have a variety of ways
they can lose quantum information,
or what we call decoherence.
Several examples of decoherence channels
are illustrated here, including charges fluctuating
on the device surface, trapped magnetic vortices,
and stray magnetic or electrical fields.
Many of these channels can be enhanced and suppressed
by the materials and fabrication choices
we make in manufacturing superconducting qubits,
as well as by their design.
Research within the superconducting qubit community
for the last 20 years has focused
on identifying and mitigating sources of decoherence
in order to improve qubit performance
with tremendous success.
We've seen more than five orders of magnitude improvement
in qubit coherence within these 20 years.
In 2018, multiple major modalities
of superconducting qubits with unique parameters tuned
for different applications have achieved coherence times
that exceed the most lenient thresholds for quantum error
correction.
This is one of the reasons superconducting
qubits are at the forefront of demonstrations today.


Patterning superconducting qubits
requires state of art fabrication technologies.
For example, at MIT Lincoln Laboratory
we fabricate superconducting qubits
in our 70,000 square foot micro-electronics laboratory.
Within this clean room, we have a full suite
of 90 nanometers CMOS tools, and we also
have dedicated superconducting deposition and etch tools.
These dedicated superconducting tools
are essential for limiting sources
of magnetic contamination, which is
one of the sources of decoherence within qubits.
When we're fabricating superconducting qubits,
we first deposit pristine materials.
And then we work to keep them as pristine
as possible by minimizing, processing, and choosing
our parameters carefully.
Many processing steps have the potential
to introduce sources of fabrication induced loss,
and we've systematically studied ways
to mitigate this potential.
There are three main steps in our baseline superconducting
qubit fabrication process.
First, we prepare substrates and deposit a pristine layer
of superconductor, often aluminum or titanium nitride.
Second, we pattern this pristine material
into essentially everything for our superconducting qubit
circuit, other than the qubit loop.
This can include readout and control circuitry,
such as resonators that interact with the qubit, the device
ground plane, and shunt capacitors,
which can store energy from the qubits.
Third, we add our qubit loops, which
contain Josephson Junctions.
Josephson Junctions are thin oxide barriers sandwiched
between two layers of superconductor.
We often use aluminum as this qubit loop superconducting material.
After we fabricate our qubit wafers,
we conduct extensive testing of the devices.
And then we wire bonded package some chips from the wafers
to cool down and measure in our dilution fridges.
We fabricate our devices on either 200
millimeter manufacturing style wafers,
or on smaller 50 millimeter prototyping wafers.
For our 50 millimeter prototyping wafers,
we focus on quickly turning around
new designs for rapid testing.
For our 200 millimeter manufacturing scale wafers,
we focus on high yield of defect free complex designs.
We now will walk through these main process
steps in more detail, and highlight at each stage
some of the key considerations, starting with preparation
of the silicon substrate and deposition of our high quality
base metal.
Silicon substrates have a surface native oxide
that is about 1 and 1/2 nanometers thick.
The silicon oxide can contain dangling bonds,
and is a source of loss for superconducting qubits.
In order to remove this oxide, we first
do a wet chemical etch, and then we load the wafers immediately
into our molecular beam epitaxy, or MBE system.
Using the MBE, we further prepare the silicon surface
by annealing at high temperature,
and reconstructing the top monolayers of silicon.
This is a molecular beam epitaxy deposition system,
and this is critical in making superconducting qubits
because it forms a very important part of the qubit,
the very base metal.
And the metal we typically use is aluminum.
This forms the capacitors, and the wiring,
and the connections to the Josephson junctions, which
form the qubit itself.
The aluminum comes from these effusion cells, which
is a really fancy tool, but all it means
is that you have a little cone shaped crucible
where you put your aluminum in, and it's
melted through these wires around the circuitry.
And the specific amount of power that goes into it controls
the temperature of the aluminum down
to under a tenth of a degree.
That means we have precise control over the vapor
pressure of the aluminum, which means
we control how fast the aluminum film is deposited
into our tool.
And we can monitor, in situ, the growth of these aluminum
films using those high energy RHEED
gun, which stands for reflective high energy electron
diffraction What this gives us is
a two dimensional diffraction view
of the surface of the wafer.
So you can see one, the silicon wafer, two,
the desorption of the hydrogen on the silicon wafer,
and three, the deposition in real time
of the aluminum on the wafer.
Next, we pattern the high quality metal
into our shunt capacitor's control
and read out circuitry and ground plane.
We pattern a layer of optical resist
onto our superconducting base metal
to define our features of interest.
The pattern is transferred into the underlying superconducting
material using either a wet chemical etch, or a plasma etch
process.
Afterwards, we strip the resist mask using a chemical stripper.
Sources of loss within superconducting qubits
can be attributed either to the materials on our wafers
or to our fabrication processing.
As a proxy for assessing the loss within superconducting
qubits, we can use coplanar waveguide resonators.
At Lincoln Lab, we use quarter wave resonators
that are capacitively coupled to a center feed line.
We deposit the same metal as our qubit base metal, and pattern,
and etch using identical processes.
Our standard chip layout has five resonators
that are each spaced 200 megahertz apart in frequency
by varying the length of the resonators.
When cooled to milli-Kelvin temperatures, which
has passed the superconducting transition point,
we can look at loss within these resonators
as a function of photon number.
In particular, we assess performance
at the single photon limit, where on average, a single photon
is in the resonator cavity.
As of 2018, we typically see single photon quality factors
of 500,000 to one million for aluminum and one to 2.3 million
for titanium nitride.


Next we'll look at fabrication of high coherence qubit
loops and Josephson Junctions.
Starting from the patterned base metal,
our next step is to lithographically define
the region where we will deposit the qubit loops
and the embedded Josephson Junctions.
We start by depositing a stack of three layers of material.
First, we spin on a layer of methyl methacrylate
resist that we use as a spacer layer.
Second is a layer of germanium, which we use as a hard mask.
For our prototyping process on top,
we coat a layer of ZEP electron beam, or e-beam resist.
We pattern the ZEP using an electron beam lithography
system to define the qubit loops.
At Lincoln Lab we use a Raith e-beam system.
The 100 kilovolts system has a 50 megahertz
clock speed, which enables reasonable write times
of our nanometer scale patterns.
I say reasonable because we raster an electron beam back
and forth across the surface of the wafer
rather than exposing full dye at a time,
like we would do in photolithography.
This definitely is a slower process than photolithography,
but we gain patterning flexibility
for rapid prototyping.
Using our e-beam system, we have demonstrated
patterning lines down to less than 10 nanometers
on the system.
And for Josephson Junctions, we routinely
patterns sub-150 nanometer features.
Alternately, we also can pattern the qubit loops using stepper
photolithography.
For manufacturing scale wafers, at Lincoln Lab,
we use a 193 nanometer wavelength ASML
scanner, which enables us to pattern
features smaller than 100 nanometers.
Optical lithography enables orders of magnitude speed
up in write time compared to e-beam lithography,
since now we are exposing much larger write areas at a time,
rather than rastering a nanometer scale
beam across the wafer.
After the resist is exposed, by either e-beam lithography
or photolithography, we transfer the pattern
into the germanium hard mask using a plasma etch.
We use plasma etching to pattern features
on a smaller scale than what you can do with wet chemistry.
You use a gas, an ionized gas, and electric field
to etch very small metal features,
silicon features, or oxide features
to make the layers in your integrated circuit.
After etching the germanium, we etch
the spacer methyl methacrylate layer using an oxygen plasma
etch.
This exposes the silicon substrate and metal contact
regions.
In addition, this oxygen plasma simultaneously
removes the ZEP top layer of resist.
In addition to defining the open area for the qubit loops,
we also pattern small germanium bridges,
where we'll pattern the Josephson Junctions.
To release the bridges, we over-etch
and undercut the methyl methacrylate.
Zooming in on a cross-sectional view of the freestanding
germanium bridge, we can schematically
show the shadow evaporation process
used to define the Josephson Junctions.
All of the shadow evaporation steps happen in situ
within different chambers of the same vacuum system.
Since we will be making superconducting contact
between the qubit loop and our underlying base metal
capacitive shunts, we first have to prepare that base layer
by removing the metal's native oxide.
To do this, we sputter away the oxide using argon ions.
We then transfer the wafer into the deposition module
and put down the first layer of aluminum.
Afterwards, we move the wafer into the oxidation chamber,
flow in oxygen, and allow it to oxidize
the aluminum for a specific amount of time
to reach the target oxide thickness.
The target oxide thickness depends on our desired qubit
parameter for the Josephson Junction critical current.
Next, we move the wafer back into the deposition chamber,
tilt the wafer to the opposite angle,
and deposit a second layer of aluminum.
We're now located at the PLASSYS shadow evaporation
system, which is a tool that we use
for fabricating one of the critical components
of our superconducting qubits.
This is where we deposit our Josephson junctions
and the associated qubit loops that surround them.
So what we do in here is four steps.
First, we load a wafer into our load box.
Then we load it into our etch chamber
once it has pumped down to vacuum.
In this etch chamber, we first ion mill
the surface as a method to prepare it before we put down
the Josephson Junction layers.
Now in this etch chamber, we're preparing that top surface
by removing the top layer, about a nanometer of aluminum oxide,
before we come in and deposit these junctions and qubit
loops.
So then we move from the etch module
over to the deposition module.
In this module, we first put down
the bottom layer of what will define the Josephson Junctions
and qubit loops.
This connects directly to that MBE material.
From there, we move into our oxidation module.
This module's job in life is to be
able to put down very pristine, very uniform aluminum oxide
layers.
It flows in oxygen into the chamber when
we have this exposed aluminum film
and it oxidizes to a very specific thickness
that we've tuned.
From there, we move back into the deposition module.
And by tilting our stage in a different way,
we're able to use are e-beam defined shadow mask in order
to create a small layer of overlap
between the bottom layer of aluminum
that's now been oxidized and a top layer of aluminum.
That layer of overlap is specifically
the Josephson Junction for our superconducting qubit loop.
From there, the process is complete
and we move back out to the load box and take the wafers out.
After shadow evaporation, we remove the wafer
from the deposition system and lift off the resist stack
in a chemical solvent.
Once the resist is removed, wafer fabrication is complete.
The completed wafer contains the superconducting qubits
with integrated Josephson junctions,
as well as base metal pattern and capacitive
shunts, the ground plane, and readout and control circuitry.


The next stage is room temperature testing.
At Lincoln Lab we do extensive automated testing
on every wafer that we fabricate.
We conduct data-driven process monitoring
to assess device performance and drive our process development.
We test each component of our superconducting qubit system.
Two examples include checking the critical current density
of the Josephson junctions and measuring the contact
resistance between the base metal
and the qubit loop shadow evaporated metal.
Each wafer is tested using an automated wafer probing
station.
After we load the wafer, we do thousands of four point probe
measurements using a 26-pin probe card in combination
with a switch matrix.
At each probing location, we apply current
to a four-wire test structure and measure the voltage drop.
The switch matrix re-assigns the current end voltage locations
for all test structures accessible to the 26-pin probe
card.
And then the probe card is lifted and transferred
to a new position where the measurements continue.
After testing is complete, the results
are automatically databased.
In addition, some devices can be selected
for further cryogenic testing, either
at liquid helium temperature of 4.2 Kelvin
or at melee Kelvin temperatures in one of our dilution fridges.
As one example of our room temperature testing,
we measure the resistance of Josephson Junctions
with varying junction lengths ranging from 100 nanometers
to three microns.
We plot the inverse of the resistance,
which is the conductance, as a function of the junction
length.
We use the slope of that plot to extract out
the low temperature critical current density, JC, of our wafer.
On our prototyping 50 millimeter wafers,
we measure the critical current density
at six identically patterned process monitor chip locations
spread across the wafer.
In this example, we targeted a critical current density
of three micrograms per micron squared.
We met that target average critical current density
and also had less than 2% cross-wafer variation.
In a second example of our test structures,
we measure contact resistance between our metal layers.
Here I show a false color scanning electron microscope
image of contact between the base MBE aluminum metal
in blue and the top shadow evaporated Josephson Junction
metal in orange.
Additionally, we also check for continuity of millimeter
long snaking lines and isolation between interdigitated combs.
We use these measurements to check for any particle defects
and for consistency of lithographic patterning.
After testing, the last step is to select wafers
for dicing and packaging.
Wafers are diced using an automated water-cooled dicing
saw.
The qubit chips are then packaged and wire bonded
to make connections from the outside cabling
to the chip circuitry.
From there, our chips are loaded into one of our dilution
fridges for measurement.


So far people have been working with small arrays of qubits,
up to around a few tens of qubits.
At some point, however, we run into a very basic problem
of where to put everything.
We want a large number of qubits that are coupled together.
But if we look back at our picture,
we can see that the actual qubit is only a small portion of what
needs to go on our chips.
We have bias lines, control lines, read out resonators,
for example.
And those can all be bigger than the qubit.
Now, you can imagine making some of these smaller.
But eventually, if you have a large array of qubits,
it's going to be hard to even get wiring
to the qubits in the center if you're
working in two dimensions.
And this is why most of the demonstrations to date
have been limited to geometries where
you can access the qubits laterally
on the surface of a chip.
This problem is not unique to superconducting qubits.
In fact, many applications have this same issue.
Consider, for example, a large scale imager
with lots of pixels.
You need to be able to get your signals out of the pixels.
But you also want to be able to put a lot of pixels
on a chip to fill a 2D array.
One way industry has solved this issue
is to move to 3D integration, where
signals are brought in vertically
instead of laterally.
We think it's necessary to move to 3D integration
to make large scale superconducting qubit circuits.
But we need to be careful when doing so,
because our qubits are affected by things
that aren't an issue with classical electronics, which
is what 3D integration was developed for.
For example, one way to efficiently route wires in 3D
is to build up a multi-layer stack of metal,
with dielectric in between so wiring on different layers
can cross each other.
But we know that having lossy dielectric materials
near a qubit can cause it to lose its quantum state.
So we've developed a new idea for how
to get the benefits of 3D integration,
the efficient wiring and ability to bring in signals vertically
without affecting the qubit.
Here's our proposed scheme, which
has three separate silicon chips that are held together
with indium bump bonds.
Within the three stack, each of the layers
is fabricated separately.
We've seen that there are process incompatibilities
between the processes in separate layers of this three
stack.
For example, we must stay at a relatively low temperature
once we've deposited shadow evaporated Josephson Junctions
on the qubit layer, the interposer layer.
However, we need to have processes
at higher temperature for the read outs
and interconnect wafer.
By separately fabricating each layer,
and combining them at the end of the process,
we have the flexibility to combine our best processes,
and optimize the capabilities of the full stack.
The top layer of the three stack contains our qubits.
Here we show two examples, capacitively shunted flux
qubits, that we use for quantum annealing applications,
and transmons, another type of qubit
that we use for gate based quantum computing.
As of 2018, state of art single qubit coherence times
for each of these styles are on the order
of 50 to 100 microseconds.
At Lincoln Lab we are simultaneously
working to further increase qubit coherence,
and to retain that coherence as we
move into the third dimension with increasing
interconnect complexity.
The second tier in the three stack
is the interposer wafer, where Through Silicon Vias, or TSVs,
that are lined with superconducting metal,
route signals between the two sides of the wafer.
The interposer provides three key benefits.
First, it provides an isolated mode
volume for each of the high coherence
qubits in order to retain coherence
times comparable to those in a planar device geometry.
Second, the interposer provides a nearby surface
for inductive or capacitive coupling
across the vacuum gap between the qubit plane
and the interposer plane.
This interposer surface can be used for control
and read out circuitry, or for coupling qubits
that bridge two devices on the qubit plane.
The third benefit of the interposer
is that it connects the qubits with the read outs
and interconnect multi-layer wafer on the bottom layer
of the three stack, while still having the qubits keep
a healthy distance from the lossy dielectrics
on that multi-layer interconnect module.
Moving down to the multi-layer read out and interconnect
layer, here we are leveraging previous work
we've done at Lincoln Lab on niobium devices.
We previously fabricated tri-layer Josephson
Junctions for superconducting qubits,
which turned out to have lower coherence than the aluminum
shadow evaporated Josephson Junctions that we use today.
We also currently fabricate fully planarized
multi-layer niobium devices with integrated tri-layer
Josephson Junctions for both Single Flux Quantum, or SFQ circuits,
as well as near quantum limited traveling
wave parametric amplifiers, or TWPAs.
For the three stack configuration
we envision embedding Josephson Junctions
within the multi-layer niobium wiring
that could be used for active circuit components,
such as on chip TWPAs.
Last, after fabrication of each of these three separate wafers,
we need to assemble the complete circuit.
To do this, we're developing a double bump bonding
approach with indium thermal compression bonding.
Indium, which is superconducting at our milliKelvin operational
temperatures, can be used both for mechanical stability
of the wafer stack and for electrical connectivity.
We align the chips using a precision bump bonder system.
We use feature in feature alignment marks, where
part of the alignment structure is on each wafer,
both during alignment, and as a check afterwards of how well we
align the two surfaces.
We have seen that we routinely achieve better than one micron
alignment between our chips.
In addition to lateral alignment,
tilt control also is critical in order
to have consistent inductive or capacitive
coupling across the vacuum gap.
Using multiple techniques, we have
demonstrated tilt control between wafers
of less than 250 micro radians.


Let's now take a deeper dive into the fabrication
of the superconducting TSV interposer wafer.
First, we fabricate the TSVs, fill them
with superconducting material, and pattern the metal
on the wafer surface.
Next, we mount the interposer wafer to a temporary carrier
wafer, flip over the TSV wafer, and remove the excess wafer
thickness down to the TSVs.
Afterwards, we add metal to this revealed surface.
And fabricate control circuitry or qubits onto that surface.
This revealed side is the surface that ultimately will
be near the qubit layer qubits.
After all the processing is complete, we dice the wafer
and release the individual chips from the temporary carrier
wafer.
At the end, the chips are available for bump bonding
into the three stack.
After the wafers are fabricated, but before we dice and release
them, we do extensive room temperature
and cold temperature testing to confirm that the TSVs are
superconducting.
Here, we see a 200 millimeter TSV wafer,
which has 52 identical die.
On each die, we have a number of TSV test structures
in addition to the active circuits that we're
using for our qubit stacks.
We use our process control monitor
chips to assess the individual metal properties,
as well as four-point probe structures to look
at both single TSVs and chains of TSVs.
As one example, we have links of 400 TSVs in series
that we can probe to assess the resistance.
When we look at the room temperature resistance
of these 400 TSV chains, we see that on average we have
37 ohms of resistance per link.
Of even more interest to us at room
temperature is that we see the standard deviation is only
two ohms, which tells us that there
is a high degree of uniformity across the wafer.
Afterwards, we took a subset of these devices
and cooled them down in our dilution fridge
to assess the superconducting transition temperature.
We saw that the devices go superconducting
around 1.6 Kelvin, and that the midpoint is 3.1 Kelvin.
This is well above our millikelvin operational
temperature.
In advance of having the full three
stack available for testing, in 2016 and 2017,
we also conducted a number of experiments
looking at components of the eventual three stack.
Since qubits are so sensitive to materials and processes,
the first experiment we did was to take
a regular single-chip qubit and design a flip chip
version of it where all the inductors and capacitors had
the same values, but the qubit chip was flipped and bonded
to another chip.
We wanted to make sure that the extra processing
and the presence of another chip bonded to the qubit chip
didn't affect the coherence time.
Here's what the circuit looked like for our single-chip qubit.
The chip has six superconducting flux qubits, each of which
is coupled to a bias line and a readout resonator.
For the flip chip version, we took all the control
and readout circuitry and moved it to another chip.
The only things left on the qubit chip
were the qubits themselves.
Then we bonded the two chips together.
The figure on the right shows an infrared image
looking through both chips and showing
that structures on one chip are well aligned
to those on the other chip.
We found that the relaxation and coherence
times of the single chip and flipped chip qubits
were virtually identical.
This is interesting for a couple of reasons.
First, it shows that 3D integration
doesn't significantly degrade qubit performance, which
is important.
Second, we've demonstrated that we can move all the control
and readout circuitry to another chip, which
is one of the things we're planning to do for the full 3D
integration scheme.
Of course, in this experiment, we
stuck with the same general design
because we wanted to isolate the effect of 3D integration.
In future work, we're planning on shrinking
the resonator and other components
so they can fit under or between qubits in a 2D array.
We're excited to be continuing to develop
further and further demonstrations using this three
stack scalable architecture.
Within both digital quantum computers and simulators,
as well as analog quantum systems,
there's a strong need for high connectivity between qubits
as well as for significant control
and read out complexity.
Although there are differences between digital and analog
quantum algorithms, both systems have
similar 3D scalability needs that
are requiring significant engineering developments.
We are planning to use this three stack
hardware to scale to test beds with 100 qubits or more.
We'll then use what we learn from these systems
as stepping stones to future larger scale demonstrations
of quantum computers.
