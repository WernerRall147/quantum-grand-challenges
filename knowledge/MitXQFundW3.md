
This week, we'll take a look at quantum algorithms and quantum
communication.
We'll start by considering the promise of these technologies,
what is needed to realize that promise, how to get there
and where we are today.
Let's begin with quantum algorithms and the promise
of quantum computers.
As we discussed earlier, quantum computers
are not smaller, faster versions of classical computers,
nor are they an incremental step in the evolution
of Moore's law.
Rather, quantum computing represents
a fundamentally new approach to processing information.
And it's the only computing model we know of today
that's qualitatively different from existing computers.
This difference and the potential promise of a quantum
computer is reflected in the fact
that simulating a quantum computer
using a classical computer requires exponential overhead.
This means that, as we add one qubit to our quantum computer,
the size of the classical computer required to
simulate it will grow exponentially.
Now we don't often experience exponential growth
in our everyday lives, and so, to gain
an intuition for how powerful it can be
you may remember the old riddle where your employer asks you
how would you like to be paid this month,
and you have two choices.
Either I'll start you with one penny,
and then each day for one month I'll
double the number of pennies, and you can keep the pennies
from the last day.
Or you can have $1 million.
Now, it's quite normal to think through the first few days
of pennies.
For example, two pennies on day one, four pennies on day two,
double that to eight pennies on day three.
And you begin to think that $1 million
is starting to look pretty good.
But in fact, if you take that $1 million,
you've lost a lot of money because the number of pennies
is growing exponentially as 2 to the n-th power,
where n is the number of days.
So on the 31st day, the last day of the month,
you have 2 to the 31 pennies.
And that's equivalent to about $21 million.
That's the power of exponential growth.
Returning to computing, if we consider the amount of memory
we would need to store all of the available states
in the state space of a quantum computer
we'll similarly see the immensity
of exponential growth.
For example, representing all of the quantum states of just 30
qubits would require at least a very powerful laptop.
Increase that to just 40 qubits and now you
need a supercomputer.
Double that to just 80 qubits and you
would need all of the classical computers we have on Earth.
And then double that again to 160 qubits,
and now you need all of the silicon atoms on Earth.
Even small increases in the number of qubits
translates to exponential growth in the amount of memory
required to represent all 2 to the n numbers
that n qubits can store.
So there's clearly a big difference
between classical and quantum computers.
And this suggests the potential for substantial quantum
advantage.
But what is needed to realize this in practice?
Basically, to realize a quantum advantage,
we need to identify the intersection
of three key requirements.
First, we'd like to identify a useful problem, one
that has practical importance.
Second, this problem shouldn't have
a known fast classical algorithm to solve it.
Otherwise we might as well just use a classical computer.
And then third, the problem must have a known fast quantum
algorithm, one that offers a substantial speed up.
Now, this sounds great, but in fact, this promise
has been largely empty, except for a small area of overlap
that we know about today.
Nonetheless, there are useful problems with a quantum
advantage, and this improvement can
be quantified using a mathematical expression.
One place is in the prefactor of that expression,
and one place is in the exponential.
The prefactor A can be a large fixed number
or it can scale polynomially with the number of qubits n.
The exponential scaling of a problem of size n
is in the exponential factor.
Either of these two types of improvement
can indicate quantum advantage.
And in the following sections, we'll
compare several algorithms and their respective speedup.

In the last section, we
saw the promise of quantum computing
and its potential for quantum advantage.
But although a quantum computer can
do anything a classical computer can do,
it often doesn't know better.
And in fact, we only have a small set of useful algorithms
at our disposal today.
So what can we do to realize the promise of quantum computing?
Quantum advantage starts with having useful quantum
algorithms, and developing new algorithms is very challenging,
in large part because quantum computers
are based on quantum mechanics.
And so developing an algorithm for a quantum computer
is quite different than doing so on a classical computer.
To understand how quantum algorithms work
and what they can do, there are currently
a couple different approaches.
One is to develop algorithms based on mathematical theorems
and their proofs.
Shor's algorithm and Grover's algorithm
are both good examples.
Based on either intuition or insight into the problem,
a quantum algorithm is first proposed,
and then it's theoretically determined if the algorithm is
efficient or not.
For example, proving that an n bit number
can be factored with high probability in a time
that scales polynomially with the size of that n bit number,
rather than exponentially.
Again, this type of development generally
requires insight into a particular structure
of the problem that lends itself to enhancement on a quantum
computer.
A second approach is to use classical computers
to simulate the behavior of quantum computers,
to glean some insight into algorithmic primitives that
can then be used to realize quantum enhancement in larger
systems.
Now, as you might imagine, simulating a quantum
computer with a classical computer is not very efficient.
After all, if we could easily simulate a quantum computer,
then we wouldn't need to build one.
Currently, classical supercomputers
with significant effort can simulate about 50 qubits.
And various probabilistic and Monte Carlo
techniques have been developed that can further
increase the qubit number in exchange
for accuracy or completeness in the solution.
Again, these kinds of classical simulations
can provide insights into how a quantum algorithm works
at small scales, so it can be leveraged in quantum
algorithms run on larger scale quantum computers.
To go beyond small scale simulations,
a third approach is to just throw caution to the wind,
build a quantum system, and see what happens.
The D-Wave system is a great example of this approach.
D-Wave's built a quantum annealer with more than 5,000
qubits, a fantastic engineering achievement.
And although there is as yet no indisputable theoretical or
experimental evidence pointing to a quantum
enhancement in quantum annealers,
there's a lot that we don't know.
And as we discussed in week one, because optimization problems
are so important, there's a tremendous application pool
to develop quantum enhanced optimization tools.
And so getting a real machine into the hands of engineers,
computer scientists, and algorithm designers
is a great way to start learning what
is and is not possible with the various quantum computing
approaches.
So developing quantum algorithms is very challenging,
and tremendous efforts have been applied to their development.
And it's because of this that we have useful or potentially
useful algorithms today.
Examples in the useful now category
are Shor's factoring algorithm and Grover's search algorithm.
Shor's algorithm can be used to break public key cryptosystems
and affords an exponential speedup
over known classical algorithms.
Doing so at a meaningful scale requires a medium-sized quantum
computer with thousands of logical qubits.
Although we don't have such quantum computers yet,
they are foreseeable, and as such, research today is oriented
towards developing new quantum resistant
public key cryptography standards,
as well as a new generation of quantum algorithms
to break them.
Grover's algorithm is related to a general class of search,
collision, and optimization algorithms
that afford quantum advantage over known classical algorithms.
However, currently, more research
is needed to help make these algorithms practical.
There are a couple of reasons for this.
One is the data-loading problem.
For example, how efficiently we can load large amounts of data
into a quantum computer so it can be efficiently searched.
In addition, there's currently a rather limited range
of problem sizes that admit benefit,
namely problems that are large enough
to make use of the quantum advantage,
and yet, not so large that it becomes practically
prohibitive to operate on a human time scale.
For example, a quantum enhancement
that reduces the runtime from a few thousand years
to a few decades is obviously a fantastic improvement,
but very few people would find that useful.
Although Shor's and Grover's algorithms are perhaps
the most well-known examples of a quantum algorithm,
it's widely anticipated that quantum simulation
will have the greatest economic impact in the future.
Simulation would apply broadly to a range of problems,
from solid state and nuclear physics to material science
and chemistry, and these are problems of importance
to both science and industry.
Classical simulations of quantum systems
are generally limited to very small problem sizes or an array
of simplifying assumptions, such as no entanglement
or semiclassical dynamics.
Exact solutions are generally intractable because the number
of variables needed to describe a fully quantum system
grows exponentially with the problem size.
It's been shown that quantum simulations are
able to efficiently model quantum systems,
and the hope is that some of these problems
may see quantum advantage on smaller scale or even error
prone quantum computers.
Whether or not this is achievable remains
an open question.
Other quantum algorithms in the maybe useful category
include sampling solutions to linear equations,
adiabatic optimization problems, and machine learning.
In these cases, the ultimate degree of quantum advantage
will depend on a number of factors,
including input/output complexity, such as the loading
problem I mentioned earlier, and making a meaningful connection
to applications.
In addition, to offer useful advantage,
these algorithms must also outperform
existing heuristics-- classical computing
methods that, while not guaranteed
to give an exact or optimal answer,
do give very high quality solutions,
and that's often sufficient for many applications.
So in summary, developing quantum
algorithms that exhibit quantum advantage
is at the heart of realizing the promise of a quantum computer.
And in the next video, we'll take a look
at the degree and type of quantum enhancement
these algorithms provide.

In the last section, we
introduced several algorithms, including
those like Shor's and Grover's algorithm, that are useful
now if we can build a quantum computer that's
large enough and robust enough to run the algorithm.
We also looked at quantum simulation,
a very promising set of algorithms which,
when realized, has the potential for substantial economic impact
and may even find utility on today's smaller scale
non-error corrected machines.
And we looked at a few potentially useful algorithms
currently under development.
For each of these examples, let's now
look at the resource requirements
for implementing an algorithm on both a classical and a quantum
computer.
This will then show the degree of quantum advantage
one can obtain by using the quantum computer.
We'll also identify the leading limitations
as they're currently known for realizing this advantage.
Let's take them in order of their applicability
as we see it today.
In this chart, we show the algorithm in the first column.
Then columns two and three show the resources
required to implement the algorithm
on a classical computer and on a quantum computer.
Now, more precise scaling functions certainly exist,
but they generally depend on the specific implementation
of the algorithm, and as a result,
they quickly become quite complicated.
So we'll simply use these ballpark scaling functions here.
Then the fourth column indicates the degree of quantum advantage.
And the last column indicates limitations
as we understand them today.
At the top of the list is quantum simulation
with application to quantum chemistry and material science.
The classical resources scale as 2
to the N-th power for a simulation of N atoms
whereas the quantum resources scale as N to a constant power
C, where C generally ranges from 2 to 6.
Now, by resources, we basically mean
both the time required to reach a solution, referred
to as a temporal resource, and the number of logic or memory
elements needed to implement the problem,
often referred to as a spatial resource.
To quantify the resource requirements,
we quote a mathematical expression for the scaling law.
That is, we're looking at how the resource requirements grow
as the problem gets larger, as parameterized by the size N,
for example, the number of atoms being simulated.
Presumably, as N gets larger, the problem gets harder.
But the question is, how does it get harder?
Does it require exponentially more resources,
such as 2 to the N-th power or a polynomial scaling like N
to an integer power.
For quantum simulation, we see that the classical resources
scale exponentially with N whereas the quantum resources
only scale polynomially.
This means that there's an exponential advantage
to using a quantum computer.
In fact, to simulate the system dynamics for a time t,
both a classical and a quantum computer
would require a similar number of time steps.
For example, if we want to simulate
the dynamics of a reaction for one second,
we would divide that one second into a similar number
of time slices.
However, the quantum advantage is
that there's an exponential reduction
in the amount of memory needed to perform
the simulation on a quantum computer,
and so the quantum advantage is exponential.
The main limitation is in determining
the mapping of a physical problem
onto the qubits, their couplings,
and the gate operations needed to implement a quantum
simulation.
Next, factoring and related number theoretic algorithms
also have an exponential scaling in the number
of classical resources, going as 2
to the N-th power and the number of digits being processed.
In contrast, the quantum resource requirements scale
polynomially as N to the third power, and so quantum advantage
is again exponential.
The main limitation, or perhaps uncertainty,
is that the best-known classical algorithm has not yet
been proven to be optimal.
So there may still be a more efficient classical algorithm
yet to be discovered.
And if so, then the degree of quantum advantage
might also change.
Sampling solutions to linear systems of equations
is the next algorithm.
In this case, we solve linear algebraic problems of the type
Ax equals b, where A is a matrix, b is a known vector,
and x is an unknown vector.
The classical resources scale exponentially as 2
to the N-th power whereas the quantum resources scale
only approximately as N, and so this algorithm also
exhibits exponential advantage.
The main limitation is related to a variety of restrictions
on the operating conditions, for example, a requirement
for a sparse matrix A.
The classical resources required for optimization problems also
scale exponentially as 2 to the N-th power, where N is again
related to the size of the problem.
However, in this case, the corresponding quantum resources
and also the quantum advantage are not well defined.
This is in part because one generally cannot determine
if the resulting answer is indeed optimal.
We can only tell if it's better than a solution we've had
previously.
Thus, we can only derive empirical evidence
that a quantum optimization algorithm provides quantum
advantage, and this is currently the main limitation
of this algorithm.
Finally, there's Grover's search algorithm
for unsorted or unstructured data.
Here, the classical resources scale
with the number of data elements N whereas the quantum resources
go as the square root of N. Thus,
the quantum advantage is square root
of N, a polynomial enhancement.
The main limitation to this type of search algorithm
is the data loading problem, namely,
how can we efficiently load in a large amount
of unsorted or unstructured data that needs to be searched.
In general, we can see that for many, if not all
of these algorithms, there can be a substantial quantum
advantage when the problem size N becomes large.
And for those with an exponential advantage,
classical computers and a Moore's law-like scaling
will never be able to catch the performance of a quantum
computer.


Just as quantum mechanics can dramatically
enhance the way we process information,
it also has the potential to enhance the way
we communicate information.
So in this section let's take a look
at the promise of quantum communication.
Communication broadly defined is the conveyance of information,
and it encompasses both sending that information
as well as receiving it.
It certainly refers to verbal communication between people
as well as nonverbal forms such as written text and signatures.
And it often comes in an encoded form.
For example, the digital zeros and ones
that are created by sampling our voices on a cell phone
or representing the words of an email that are then routed
from one computer to another.
In fact, even information on a chip
must be shuttled around, communicated
between a processor and its memory.
And this concept can even be extended
to include several spatially distributed
computing nodes, all of which are available to attack
a particular problem, but must be coordinated and therefore
require communication between these different nodes.
All of these are examples of classical communication.
But quantum communication is different,
and it represents a fundamentally different means
to encode, convey, and authenticate information.
These differences and the potential promise
of quantum communication are reflected in three basic facts
or theorems.
The first is that classical information encoded in qubits
can be transmitted two times faster than by classical means.
This is achieved using a concept known as superdense coding,
and it's a provable quantum enhancement.
Basically, two bits of classical information
can be transmitted using a single qubit when
that qubit is part of an entangled pair of qubits called
a bell state.
Now, that's, of course, two qubits,
but I only needed to transmit one of them
to send two classical bits.
That's superdense coding.
The second is that quantum bits cannot be copied or cloned.
And it's, again, a provable consequence
of quantum mechanics.
Now, of course, if I prepared a qubit in a given state,
I know that state and so I can prepare a second qubit
in the same state.
But if I have a qubit in an unknown state,
I can't make an exact copy of it,
and that's called the no cloning theorem.
The third fact is that attempts to intercept or measure quantum
bits can be detected.
Clearly, those bits cannot be duplicated by the no cloning
theorem.
And so an eavesdropper must make some kind of measurement
in order to glean any information.
And it's the measurement process that
always leaves a signature that's detectable in some way.
So what is needed to leverage these three facts
and realize the promise of quantum communication
in practice?
Well, to realize quantum advantage we
need to identify problems at the intersection of three
key applications.
The first is to find a problem that
can leverage the enhanced capacity to encode information
that's enabled by quantum mechanics.
Second, there are problems related to authentication.
The ability to confirm the identity of an individual
or the truth of a particular attribute.
And third are problems associated with collaboration,
collaboration between people or agents such as secret sharing
or game theory.
For example, enhance means to auction
or to vote without attribution.
Or using quantum mechanics to verifiably share
public goods in a way that avoids
certain rational yet self-destructive tendencies
such as the tragedy of the commons.
Realizing the promise of quantum communication
will require finding problems that exhibit quantum advantage.
And in the next section, we'll take a look
at several such problems.


In the last section, we discussed
the promise of quantum communication
and its potential for quantum advantage.
That advantage was based on three tenets of quantum
mechanics, namely quantum-enhanced channel
capacity, a concept known as superdense coding,
the no cloning theorem, which forbids
copying an unknown quantum state,
and a form of communication non-disturbance, by which
any attempt to intercept or measure quantum bits
can be detected.
We can begin to understand how these tenets enable
the promise of quantum communication
by considering the number of participants simultaneously
participating in that quantum communication.
The first example is point to point secure communication
using quantum key distribution.
Secure communication relies on the use of a private key,
essentially, a string of bits that's used
by a cryptographic algorithm.
Quantum key distribution provides
a means to securely transmit and share such a secret key.
The secret key can then be used to encrypt and decrypt
information.
Any attempt to intercept that key can be detected,
and when this happens, the compromised bits
are simply discarded and replaced
with additional secure bits.
In this way, quantum mechanics enables two parties
to communicate securely.
In addition, as we'll learn later,
quantum mechanics can also be used
to generate true randomness, a resource
for many cryptographic applications and a step
above existing classical pseudo-random number
generators.
Second are applications involving a few participants.
One important example is quantum secret sharing amongst, say,
two or more people.
Let's say Alice wishes to send a secret to both Bob and Charlie,
and she would like them to learn that information
simultaneously, so that neither Bob nor Charlie can
have an advantage over one another
by learning the secret first.
By using quantum communication to distribute
an entangled state that's shared between Bob and Charlie,
Alice has created a situation where
Bob and Charlie must coordinate to uncover what that secret is.
They can coordinate on an open classical channel,
but quantum mechanics will ensure that they receive
the information simultaneously.
Finally, a third set of applications
involves multiple distributed participants
or multiple distributed computing
nodes that, in concert, perform a quantum algorithm.
One example is quantum scheduling,
which uses Grover's algorithm to search for a time
when n distributed people are available.
Another example is related to distributed computing systems,
such as the leader election problem.
In this application, a unique leader or a master node,
must be chosen from amongst all of the distributed computing
nodes.
In both cases, it's known that quantum communication
and quantum computing together provide an advantage
over classical approaches.
Despite the promise and numerous examples
of problems where quantum communication gives
an advantage, there are only a few examples
of practical applications to date.
One application that's available now, even commercialized,
is quantum key distribution or QKD.
In QKD schemes, Alice and Bob want to share a private key,
and any attempts by Eve to intercept it can be detected.
There are demonstrations of QKD using photons
over 100 kilometers of optical fiber
and even a demonstration of transmitting signals
between two points on earth using satellite quantum
communication.
In fact, QKD even serves as a foil
to quantum codebreaking by Shor's algorithm.
As we've already discussed, Shor's algorithm
can efficiently break RSA public key encryption.
In fact, it's also efficient against
Diffie-Hellman key exchange and elliptic curve
cryptographic schemes.
However, messages encrypted using a one time
pad are, in principle, secure.
One time pad schemes use each bit in a key
only once and then discard it.
They therefore need to be continually renewed,
and this can be done securely with QKD.
The main issue with QKD security is
that, as with most cryptographic schemes,
there are many channels for attack.
For example, one must generally control access
to the hardware that's used to implement a QKD scheme.
Another limitation is signal attenuation.
Classical communication links use repeaters to regenerate
and amplify a signal.
However, due to the no-cloning theorem,
this is not so straightforward with quantum communication.
Instead, as we'll learn later in the course,
a quantum version of repeaters has
been proposed that can effectively
extend communication lengths using quantum teleportation
and distributed entanglement.
In conjunction with quantum memory,
distributed entanglement would enable a quantum communication
link to be established.
Other applications that may be useful
include quantum secret sharing, auctioning or voting
without attribution, the use of verifiable quantum digital
signatures, and message authentication.
For all of these examples, developing robust protocols
and hardware systems that are immune to compromise
will be necessary to fully realize the promise of quantum
communication schemes.


In this case study, we'll hear from
several leading industrial and start-up efforts targeting
quantum computing.
We approached several companies, and we asked them
for their perspectives on the business, engineering, science,
and technology of quantum computing.
To get the discussion started, we
asked a number of baseline questions.
First, what technological approach
are you employing to realize quantum computers, and why?
Second, what is the business application
you have in mind for the quantum computing systems
you are developing?
Third, what are the major technical hurdles
you're facing?
Fourth, how will your approach contribute to the advancement
of scientific knowledge?
And fifth, what other industries are either vertically
or horizontally integrated with respect to your own efforts?
We also invited these companies to add
in other perspectives and thoughts not captured
in these questions.
The results are very interesting and informative.
And so with that brief introduction,
let's hear directly from several of the major commercial players
in quantum computing today.

STEFAN NATU: Now, at AWS, in 2019, we
made the decision to launch a quantum computing program based
on the industry consensus at the time
that near-term quantum devices, or NISQ devices,
may provide commercial value.
We launched our quantum computing strategy
with two major threads.
The first is a focus on building our own hardware.
And that's a long-range effort that's
focused on error correction.
And the second is a cloud service
to provide customers access to near-term quantum
hardware from third-party quantum hardware providers.
And that's called Amazon Braket.
Now, the goals of Braket are to engage customers early
and prepare customers for the arrival
of these fault-tolerant quantum machines.
In the long run, we will be hosting quantum computers
in our data centers and give customers
access to quantum computing resources
alongside on-demand elastic and scalable
CPUs and GPUs via the cloud.
Over the past four years since we launched Braket,
thousands of customers have executed
many billions of circuits on real quantum computers.
So you might be wondering, what have we
learned from all these experiments?
Today I want to tell you about four key learnings.
The first one is that it's too early to call winners.
Now, in this course, you have no doubt
learned about the different modalities of quantum computing.
It is too early to predict today which of these modalities
is ultimately going to deliver advantage
for commercially relevant problems
over existing classical techniques.
Each of these devices have unique characteristics
that make them suitable for certain workloads.
For instance, superconductors are fast,
whereas trapped ions have all-to-all connectivity.
And that's why our strategy at AWS
is to reduce technology risk by providing access
to a diverse range of hardware devices.
Similarly, today, when customers try
to experiment with different hardware,
they're often required to learn the software stack
of the providers separately.
This slows down innovation and experimentation.
And so on Braket, you can experiment
on multiple machines with as few lines of code change
as possible.
The second learning is that disruptive technologies
demand incremental innovation.
When fault-tolerant quantum computers arrive,
everyone's expecting a sort of ChatGPT moment
when the industry is just going to take off.
But the reality is that innovation is incremental.
The first experiments on using neural nets
for large-scale image recognition tasks
occurred in 2012, and OpenAI released ChatGPT in 2022.
So from 2012 to 2022, tens of thousands of developers
were building novel neural net architectures
and training and iterating ML algorithms
that have made today's GenAI innovation possible.
And we see a similar trajectory for quantum.
Application development needs to happen hand in hand
with hardware technology improvements,
as developers need to build the software
stack and the tools that are needed to enable
those end-user applications.
What this means is that there's opportunities for you
to innovate up and down the stack,
get a firsthand sense of the state of play of the industry,
and determine what the potential applications that might
be disrupted by quantum and what are the limitations of today's
devices that need to be overcome before they become useful.
It's essential to get started with exploring
the nuances of the hardware and the software stack
that's needed to program these quantum computers.
As the hardware improves, what they are capable of
is going to change.
And you all have the opportunity to be that change agent.
So today, you can go and get a digital badge
by taking a free online training course on quantum on AWS.
Once you do that, you can go ahead and apply for an AWS Cloud
Credits for Research grant to get
going with using quantum hardware on AWS.
The third learning that I want to talk about
is that quantum is not going to develop in a vacuum.
Just like a GPU today works in tandem with CPUs,
a QPU, or a Quantum Processing Unit,
will work in tandem with many GPUs and CPUs
to run industry-relevant applications,
whether those are material science simulations
or optimization problems and so on.
And it's highly likely that the earliest applications of quantum
computing may require large amounts of classical code
processing power.
So it's super important that when
you're selecting a platform to experiment on,
to ensure that you think about this holistic picture and not
just think about the QPU itself.
At AWS, that was a question we debated for a very long time.
Should we launch Braket as a standalone service outside
of AWS, or should we make it an integral part of the AWS
platform?
We decided to go with the latter.
Because when quantum computers are
working as an integral component in a hybrid HPC infrastructure,
customers that are running those business-critical applications
will care about the security, the networking infrastructure,
the encryption of their data at rest and in transit,
and ensuring that the proper permissions and guardrails exist
around who accesses that data and ensuring that their quantum
infrastructure provider is compliant
with the various compliance attestations
that they need to meet.
So you can say that in some sense,
our goal is to make quantum as boring as possible,
meaning that you can just focus on building that end
application.
Our fourth learning is that ecosystems
play an essential role.
On EC2 today, which is our compute service in the cloud,s
we offer customers a choice of hardware, from Intel, AMD,
NVIDIA, and our own.
And we envision the same to happen in quantum computing.
So our role is to enable you to push the innovation forward,
break down those barriers for you to do so,
and cultivate the ecosystem.
Today, there are dozens of quantum software partners
who are building middleware technologies, such as error
mitigation, and exploring early applications with enterprise
customers.
We actively encourage these partners
to build on top of our service.
They have application-specific expertise
that enables them to understand the potential benefits
and pitfalls of quantum computers
for use cases that are relevant to industry.
Today, the most prominent use cases for quantum
are in materials science, chemistry,
such as molecular simulation, financial services,
such as portfolio optimization, logistics, and machine learning.
Some of these are more near term than others,
but they are being actively explored
by many of the partners who are on our ecosystem.
So what can you do?
Like I said, this is all about experimentation.
It's about moving the ball forward
with incremental improvements and keeping a close eye
on the state of the art.
We firmly believe at AWS that quantum will one day
solve problems that are forever out of reach
of classical computers.
And I'm excited to be a part of that journey.


JERRY CHOW: Computers are everywhere and in everything.
They touch every aspect of our lives.
And there doesn't seem to be a limit to their power.
But the truth is, there are some very hard problems
that even our most powerful classical supercomputers
will never be able to solve.
We believe that quantum computers
will be able to start tackling some
of these problems in a few short years.
Here's an example.
Today, improving battery technology
is incredibly time and labor intensive.
Researchers believe that quantum computers will soon
be able to run much more powerful chemistry
simulations, which we hope can be used to radically improve
battery efficiency.
Imagine an electric car that only needs to be charged once
a month, not once a week, not once every few days,
or machine learning.
A 2023 Nielsen report found that credit card fraud
cost the financial industry $33 billion globally.
Quantum machine learning algorithms
could extend our ability to perform
the higher-dimensional data processing that
would allow us to improve fraud detection by reducing
false positives, which are very costly.
Right now there isn't a quantum computer
on the planet that can beat all classical methods
at these kinds of problems.
But we think that's about to change.
Looking ahead, our work is really
focused on building the devices and software
tools that let us run larger and larger circuits that
are comprised of more qubits and more logical gates.
In 2016, IBM became the first organization
to take quantum computers out of the research lab
and put them in the cloud.
The first offering provided free access to a 5-qubit IBM quantum
Canary processor for anyone with an internet connection.
Now, less than a decade later, in 2023,
an IBM experiment showed that exact classical methods could
not simulate a circuit comprising just over 100 qubits
and just under 3,000 gates.
Classical computers can only approximate that level
of complexity.
So how do we make this journey from 5-qubit processors
to the 100-plus-qubit processors of today?
Well, back in 2016, we had no guarantee that we'd ever cross
the 100-qubit threshold.
But we knew that if we wanted to get there,
we'd have to make a lot of progress
on three key metrics, scale, quality, and speed.
Scale is the number of qubits in our processors
and in the quantum chips that we run.
Now, quality is determined by the error rates
that we see in our quantum logic gates and that act
on two qubits at once.
These underlying 2-qubit gates have an enormous impact
on performance across a large quantum device.
This quality actually determines the size of the quantum circuits
that we can execute faithfully.
Now, speed has to do with the number of circuits
that a quantum computer can run per unit of time.
Fastest circuit runs gives us more space to handle errors
and makes it more practical for researchers
to actually incorporate quantum into their workflows.
In addition to improving the scale, quality,
and speed of our systems, we also
knew that we would need to begin working on new quantum
algorithms to make the best use of our evolving systems.
This is a big job.
And we've enlisted the help of the entire quantum community.
But there's still a lot of work to do.
At IBM, we've built a tool to help
us think about what comes next.
We call it the IBM Quantum Roadmap.
The IBM Quantum Development Roadmap map
shows how our systems will grow in terms of qubit count
and the size of the quantum circuits they can run,
which we measure by the number of gates
that we can execute accurately.
Here you can see where we started, with the launch
of the IBM Quantum Experience.
You can see some of the small systems that
were available during those first few years,
like the Canary and the Albatross.
In 2021, we crossed the 100-qubit barrier with Eagle.
And then in 2023, we broke the 1,000-qubit barrier with Condor.
From 2023 to 2024, we also debuted two versions
of the IBM quantum Herron chip.
Now, Herron doesn't have as many qubits as Condor,
but it's the first to be capable of returning accurate results
on a quantum circuit all the way out to 5,000-qubic gates,
an important milestone.
And it demonstrates a significant improvement
in the underlying quality through using
a novel tunable coupler architecture.
Then we have the IBM quantum flamingo,
which are largely based on modularity scalability
of quantum processors.
It's actually made up of two Herron chips joined together
by four connectors, which we call L couplers.
We're going to continue to iterate on Flamingo, improving
its underlying performance.
From there, we'll introduce Starling in 2029
and then Blue Jay in 2033.
These systems open up a whole new world of potential quantum
applications because they'll be our first quantum
processors to actually demonstrate full quantum error
correction.
Quantum processors create incredibly delicate quantum
states that are really susceptible to errors
that can be caused by noise in the environment.
Today, we have error handling methods such as quantum error
mitigation, to extract useful data from noisy outputs.
But true quantum error correction
will be much more powerful.
By using error correction codes, where
we encode qubit information into a larger set of qubits,
we expect that we'll be able to suppress logically-encoded error
rates to significantly lower levels.
Now, in 2023, our quantum error correction theory team
devised a highly efficient and effective new code,
beating other leading approaches by an order of magnitude
in terms of needed physical resources.
This led us to mark our targets in our roadmap for Starlink
and Blue Jay to achieve 200 qubits and 100 million gates
by 2029 and 2,000 qubits and 1 billion gates by 2033.
But quantum computing is about more than just hardware.
2017 we launched the Qiskit SDK, our open-source software
development kit.
In those early years, execution for quantum computers was slow.
So in 2021, we introduced Qiskit Runtime, a cloud-enabled runtime
environment to enable more efficient workloads
with higher throughput.
In 2024, we introduced Qiskit Code Assistant and the Qiskit
Functions Catalog.
The code assistant helps developers quickly generate
high quality quantum code, while the functions catalog gives us
a collection of pre-built services
that allow users to abstract away parts of the quantum
software development workflow.
We plan to continue growing the collection of services
available in the Qiskit Functions Catalog.
We launched scalable circuit knitting.
Circuit knitting is a technique that breaks down one quantum
circuit into multiple smaller circuits
and then runs them in parallel on multiple quantum processors.
And this will all be put together
in a new paradigm, which we call quantum centric supercomputing,
where we leverage high-performance classical
computing systems, to help partition and also reconstruct
larger quantum circuits.
This all sets the stage for us to succeed
in building Starlink and Blue Jay in the later years.
Now, despite the achievements of the past few years,
we haven't yet found a problem that quantum computers can solve
cheaper, faster, or more accurately
beyond all classical approximation methods.
And this is a milestone that we call quantum advantage.
So why are enterprise research organizations, government
agencies, and academic institutions all investing
in working with IBM quantum today?
Well, by 2035, McKinsey & Company
predicts that quantum computing technology
will create as much as $2 trillion in value.
And a report by Boston Consulting Group
indicates that as much as 90% of that value
will go to the early adopters.
That's why research organizations are starting now.
There's a steep learning curve.
So an early start on learning and experimentation
can provide a substantial competitive advantage.
Organizations work with quantum service providers,
like IBM, not only to gain access to our systems,
but also to gain access to our technical and managerial
expertise.
All of our clients and partners are helping us as well.
When quantum advantage is first achieved on our system,
it will likely not be done by our own researchers,
but more likely by domain experts
at one of those partner organizations.
We couldn't possibly dream up every experiment
that's worth trying.
We need our wider quantum research community
to help us explore the potential of large-scale quantum computers
from all these different angles.
And it's why a big part of what we offer
is also open access to our systems.
It's why we've built the Qiskit software development
kit as an open-source tool that anyone can use for free.
We want to ensure that these resources are
accessible to anyone in the quantum community.
And we all have to work together to pursue quantum advantage.


JACK HIDARY: Hi, my name is Jack Hidary.
I'm Founder and CEO of SandboxAQ.
When I was recruited to Alphabet about seven years ago, what
we realized is that advanced compute was good not just
for solving search, but we can now
train our eyes on so many of the large problems in the world.
With our growing success, we realized
that we can have deep impact at scale, deep impact in areas
such as health care and drug development,
hitting major diseases; deep impact in the energy
sector, automotive and aerospace;
deep impact in navigating without GPS, which
is a critical issue in the world today;
deep impact in cybersecurity, protecting the world's data
from the threats of both AI and quantum.
We realized that both AI and quantum
would be two critical tools in solving these challenges.
When we think about AI, we can go beyond just large language
models into new models that are actually quantitative in nature.
This takes us beyond the kind of GPTs
that you see out there to large quantitative models,
LQMs, models that understand physics and chemistry
and biology.
These models are very, very different
than the models you see out there on the internet,
but they're really the right tools
to use to develop new treatments for diseases like Parkinson's
and Alzheimer's and cancer.
They're the right tools to think about new battery chemistry
to store energy.
They're the right tools for the new materials
we need to solve key issues in our world.
And so when we started developing these kinds of tools,
we started getting more and more success.
We realized that we can work on real pharmaceutically relevant
molecules.
We can start to work on materials
that would affect and impact the automotive area,
the aerospace area, and other key industries.
And so we decided to spin out the company
as an independent company to grow faster and further.
So how does SandboxAQ accomplish these key goals?
How do we impact drug discovery and development?
How do we impact energy storage and generation?
How do we impact material science
for so many critical industries?
Well, it starts with understanding the need
to combine AI with physics.
Our world is governed by physics.
And we need to train AI in that physics
if we want to impact that world.
I'm sure you've all heard about large language models
and tried some of those online.
We have that here on the slide in the green--
AI for language and graphics and videos,
a lot of interesting use cases there, such as marketing copy,
interactive customer service applications, software coding.
It definitely helps with that.
But when it comes to the real world, when
it comes to the physical world, when
it comes to quantitative finance,
we need a different kind of AI, an AI that's
combined with quantum physics and other key tool sets
to understand how to make stuff for that world,
and also to optimize portfolios and other applications.
As you see on the slide, the largest sectors of our economy--
the largest sectors, including financial services, biopharma,
auto and aerospace, chemicals, energy and materials,
these are the ones where there's some application for language
models.
But really, what we need are quantitative models, models that
understand the equations of quantum physics,
models that understand the equations that
govern so many key areas and sectors of our society.
These are the models that SandboxAQ focuses on.
We are the global pacesetter in these areas
and develop models now for each of the sectors
that you see on the slide.
So what does the future of computing look like?
As you see on this slide, it looks
like a combination, a mesh, of both the work
that we do today on GPUs, from NVIDIA and many other companies,
as well as the interaction with QPUs, quantum processing units.
In this course, you've heard about different ways
of building quantum computers and using quantum computers.
But they will exist in a mesh in a hybridized format
with the classical computing of today.
There's a role for both of these as we move forward,
and much of that will be in the cloud.
Quantum computing is one of the first innovations that
is cloud-native, born in the cloud.
99% of how people interact with quantum computers
today and tomorrow will be via the cloud.
And those same clouds is where we host
most of the GPUs of the world.
And so when you write a program that
is meant to look at drug discovery, part of that program
will run on the GPUs, and part of that code
will run on the QPUs.
They'll be integrated into one mesh, resulting in a solution
that neither alone could produce.
Let's look at an example in practice.
On the screen now, you're looking
at a molecular interaction.
The small molecule in purple is going
through thousands, perhaps millions, of permutations
to fit into a larger molecule, in this case, a protein.
This is very typical of the kind of work we do in drug chemistry.
And these interactions are molecular in nature
and therefore quantum in nature.
This is the kind of work that is accelerating drug chemistry
by many, many years and providing leapfrog innovation
in this particular sector.
Let's now look at another sector, navigation.
What happens in navigation when you don't have GPS?
We all rely upon GPS in our phones
and our cars and, of course, planes also rely upon GPS.
But what if GPS is jammed?
What if it's spoofed?
And that's happening right now.
Russia is jamming GPS over much of Europe.
China's jamming GPS over much of the Pacific area,
particularly over Taiwan.
And Iran is jamming GPS in the Middle East.
What if you have to navigate in these areas?
Well, it turns out you can navigate.
And the inspiration, of course, comes from the animal kingdom.
Birds and whales and many other animals
have the ability to navigate via the magnetic field of the Earth.
And now, thanks to this innovation, humans do as well,
this innovation where we're applying quantitative AI
to look at the magnetic field of the Earth.
We're using quantum-based sensors
to pick up the small changes from one area of the Earth
to the next, similar to our fingerprints,
unique every single different spot.
And we're using this MagNav, magnetic navigation,
to help that plane navigate even when there's no GPS.
So this is another example where AI and quantum interact
to provide a new solution that was not possible before.
And so these two case studies, both in drug chemistry
and in AQNav, provide examples of the leapfrog innovation
that happens when you bring AI and quantum together.
Thank you.

BEN BLOOM: We're building quantum computers
using arrays of neutral atoms.
We do this because we believe the technology is scalable
and can reach a level that actually accesses utility scale
problems.
One of the amazing things about neutral atoms
is how it's actually built off of technology
that already exists.
What we do is we take qubits and we use classical hardware,
and that classical hardware is almost
like projection equipment.
So we build this projection equipment
that we can control really, really quickly and actually
manipulate these atoms at the atomic level
so that we can actually control their state,
entangle them, and perform those calculations.
REMY NOTERMANS: In order to build a fault tolerant quantum
computer, we need the performance of qubits
to be many orders of magnitude better than what it currently is
or what's even achievable with the qubits themselves.
So in order to do that, we actually group multiple
physical qubits, in our case neutral atoms,
together and create a so-called logical qubit that
has much better performance than any of the individual
qubits themselves.
For most applications that people are talking about,
you need hundreds and thousands if not more logical qubits
to run these fault tolerant applications.
So one of the big advantages of our technology
is that through a clever optical engineering,
we can really scale the number of physical qubits
extremely aggressively, where you can really
enter the era of scientific and economic advantage
for running quantum computers.
BEN BLOOM: One of the things we're really focused on
is making sure that we can get to utility scale.
So at every step of the way, we want
to make sure when we build systems,
we're increasing the amount of qubits
we have tenfold every single generation so
that we can get to utility scale as fast as possible.
KRISTEN PUDENZ: Not only are we pushing for system scale,
we're pushing for usable systems,
and that means that we need to be
able to run long computations, get meaningful results from them
and be able to use those results to inform the science
problem or the industry problem that began the question.
So we look at all of these things,
and we believe that our systems will be very
capable of making an impact.
JUSTIN GING: Doing optimization problems, simulation,
or acceleration of machine learning,
almost every industry has some way that they could
benefit from quantum computing.
We are working together with the National Renewable Energy
Lab located in Golden, Colorado, and they
have a digital twin of the energy grid modeling
out everything that goes into it.
And as much as possible, they like
to automate how to handle different situations.
So with this digital twin, they have found certain applications
where quantum can work in a more effective way than classical.
Another area where we've partnered
is with the University of Colorado Anschutz Medical
Campus, where they're looking at things like can we use quantum
to help in the machine learning process of identifying disease,
particularly in the ophthalmology,
looking at diseases of the eye.
And we're also working with a large international bank,
looking at portfolio optimization and pricing
of exotic options and using quantum
as a tool in the finance field.
KRISTEN PUDENZ: Quantum chemistry applications
are excellent candidates for running smoothly
on quantum computers.
We think about things like nitrogen fixation.
This is a process that provides the fertilizer that we
use to feed the world or catalysis that
makes all kinds of processes more energy efficient and able
to produce scarce materials more easily.
Huge potential for optimization problems
like the traveling salesman problem
when package delivery services come
and try to bring things to your house and your neighbors.
How do they do that the most efficiently?
If we can provide even small margins and savings
on the routes that those vehicles follow,
we should be able to provide a large degree
of industrial value.
JUSTIN GING: There will probably be organizations
that find a particular application that's
crucial to their business, and they'll
implement quantum resources to on a day-to-day basis
be constantly churning out particular types
of applications.
Maybe a bank that needs to reprice a portfolio just
on a rolling basis can now do so faster,
more efficiently change their business processes.
REMY NOTERMANS: In the long term,
quantum computing will be integrated
as some hybrid compute resource together
with supercompute centers or other HPC centers
and really provide a background black box hybrid computing
resource that a lot of people will be using without really
realizing which part of the application that they're trying
to run is actually being run on a quantum
computer versus another cloud resource.
KRISTEN PUDENZ: We engineer our roadmap and the system
generations therein to not only represent achievable advances
in technology but to address application projects that
have real impact and real meaning to society.
BEN BLOOM: We're really going to start
trying to answer the questions that the customers are really
asking.
They're not just asking can I run this simple algorithm.
They're asking can I build this new material.
And that's where we really want to go as a company,
pushing towards actually giving solutions, not just giving
answers to algorithms.


ROBERT SCHOELKOPF: Quantum information
is a fascinating and exciting field.
It's a completely new paradigm for how we store and process
information.
And it has the promise to address
certain kinds of problems that could never be solved
on conventional computers.
We've come an incredibly long way
in the last couple of decades.
When we started in the 1990s, there weren't even qubits.
At Yale, we've helped pioneer the field of circuit quantum
electrodynamics.
This is a way in which we can have
artificial, man-made elements that
behave like individual atoms and photons.
And with this approach, we can access all the special features
of the quantum domain, like superposition and entanglement.
This approach has allowed new explorations
in quantum optics, quantum measurement and quantum control.
And today, it's an emerging technology
with multiple machines available on the cloud which
allow you to log on and run your own quantum computations.
The challenge for the field today
is to scale in a useful way, and thereby
realize truly revolutionary computing power.
This requires making our computations
more robust through the magic of quantum error correction.
Here at Quantum Circuits, we focus
on the problem of detecting and correcting the inevitable errors
at the hardware level.
We do so with hardware-efficient approach
that involves having error detection built into the qubits.
In the rest of this video, we'll explain to you
how this unique approach works.
ANDREI PETRENKO: At Quantum Circuits,
we follow the circuit QED approach to quantum computing
With superconducting qubits, we use both transmons and unique
element, that is the 3D cavity.
3D cavities are great because they're high-coherence elements,
and they enable us to do high-fidelity gates.
And we actually use them, in addition,
to build these things called dual-rail qubits, which
have been around in the industry for a while, typically
in the context of photonics.
But what we do is we build them as kind of novel units
that have a number of components in them, including transmons.
We make them the physical qubits in our quantum computers.
Now, what this enables us to do is,
given the fact that single-photon loss is
the dominant error mechanism in cavities, way
beyond any other error like dephasing or bit flips or phase
flips, we can convert single-photon loss
into erasures.
And erasures are a really interesting type of error
because you know when and where that error occurred
in the circuit.
And what that allows us to do is perform things
like error detection.
And with that error detection, that gives us some novel tools
to take us down the path toward error correction
in New and interesting ways and leverage both existing codes
and think about new codes that will give us
new paths toward greater efficiency.
There are a number of challenges that we're
going to have to overcome, both as quantum circuits,
but also as an industry, to get to successful quantum computing.
So as you heard me talk about error correction before,
that's a really key topic in the industry.
That's one of the reasons we've been focusing on error detection
as a key stepping stone and milestone toward that end
with dual-rail qubits.
We're providing low-level access to erasure data in our devices
that doesn't get abstracted away.
We think this could be useful for researchers, in particular,
to understand more about noise models, error models,
and thinking about error correction codes
using photon loss and erasures as the basis.
We put out a publication in 2022 about random walk phase
estimation.
It was co-published with Microsoft's team,
and it was based on theoretical work
by Nathan Wiebe and Cassandra Granade.
It highlighted how real-time control can really yield
benefits in quantum algorithms.
We're really looking to extend those results to see
how they can benefit from quantum error detection going
forward.
We're not specializing in any single industry today.
And to take a couple of concrete examples,
we have optimizing cargo loads on airplanes or even portfolio
optimization with, let's say, Monte Carlo methods in finance.
All of those have really important implications
for how we function as a society.
And that's really going to make an impact on us
over the next 5, 10, 15 years.
So thank you for listening to the course.
Thank you for being a part of this journey
and for listening to our industry perspective.

DAVID RIVAS: Rigetti is a full-stack quantum computing
company focused on superconducting qubits.
What that means when we say "full stack"
is we build everything that we actually have to build a full
quantum computing system.
That includes the chips.
That includes the hardware that goes inside the dilution
refrigerator.
That includes the control systems.
It includes quite a lot of software
for making the system available to end users.
We spent an awful lot of time both with architecture
and tuning process.
Every little change in almost every component of the system
can begin to make an impact on the performance.
So having a captive fab and doing a lot of this work
ourselves turns out to make a very impactful difference,
both in the kinds of things we can do
and the speed within which we can do them.
Two of the most interesting and important breakthroughs
that we've made relate to packaging.
We were the first to do superconducting qubits with full
3D signaling.
This enabled us to get denser, which helps with scaling,
but it also enabled us to put a lot more control in terms
of the kinds of interactions that we were having
with the underlying qubits.
Similarly, we were the first organization
to ever build out functioning quantum processors
with multiple dies, achieving entanglement
across a processor boundaries, fundamentally a packaging issue.
As we move into an error correction world,
this concentration on packaging, along with underlying processing
and qubit architecture, will become more and more important.
ANDREW BESTWICK: One of the benefits
of having our own fab is that we can have quantum scientists
and fabrication experts as part of the same team,
and there's a frequency and depth of dialogue that can lead
to interesting breakthroughs.
A recent example of this is a breakthrough
we had called alternating bias-assisted annealing.
One of our scientists had a burst of insight
one day about how to reduce the variability of the Josephson
junctions in our chip, which determine
the frequency of the qubits.
He grabbed one of our fab gurus.
He laid out the idea, and this resulted in the ABA process.
That led to a big breakthrough.
We were able to cut down on the amount of spread
in our Josephson junctions, the amount of manufacturing
variability, by almost a factor of 10, which
got our frequencies more precise by almost a factor of 5.
And that led to all kinds of new opportunities
to really precisely engineer the Hamiltonians of our chips.
MIKE PIECH: One of the biggest reasons why organizations
acquire our systems is to carry out
their own experimentation with quantum computing,
and in particular playing with the construction of quantum
computers.
Entities such as national laboratories and supercomputer
centers have initiatives around getting
familiarized with different quantum computing modalities
and what it takes to set up and operate systems
based on those modalities.
There are also some universities that
don't have the fabrication or other large-scale facilities
necessary to make all the quantum hardware from scratch,
but which nevertheless want to expand programs
in quantum computing.
MARCO PAINI: The application development
we see continues to be dominated by use cases that
have been discussed for many years, quantum
simulation, optimization, and machine learning.
Quantum simulation is mostly molecular modeling
or condensed matter related to discovering new drugs
or engineering new materials.
Optimization algorithms are applicable
in a wide range of domains, from logistics to finance.
An area where there continues to be exciting development
is quantum machine learning, for example, quantum feature
mapping in its combination with classical methods such as kernel
methods.
Feature mapping is a transformation
of the input data into a different form
in order to improve the performances
of a downstream learning model.
Quantum feature mapping is the realization of a feature
map with quantum circuits.
An example of the combination is a project
we did with Moody's and Imperial College London.
We used a combination of quantum feature maps and signature
kernels on historic economic data
to train a model that shows promising improvement
in predicting recessions when compared
to classical alternatives.
This work is ongoing and continues
to offer promising benefits.
ANDREW BESTWICK: Most challenges fall
into two categories, fidelity of each
of the operations on the chip and scaling,
how to get as many qubits and operations as possible
into a single system.
The fidelity numbers are determined
by how long the qubits live, what their coherence times are,
and so we're always trying to make the qubits' materials as
good as possible, so their lifetimes are as long as
possible, and find the most advanced ways of operating
our gates so that the operations are fast and you can get as low
of an error rate as possible.
For scaling, one of the obvious challenges
is getting chips with lots of good qubits on them.
Our approach is to make small chiplets and to combine them
together to form coherent quantum circuits.
There's also lots of challenges with getting signals
onto the chip.
We have a 3D integration chip architecture that allows us
to deliver signals directly vertically down onto a qubit
through silicon vias that are superconducting.
We use a flip chip cap bonding process
to put a whole new layer of electronics right
on top of the qubit, and we have a superconducting interposer
approach that allows us to get signals
onto and off of the top of that chip architecture
in a way that is coherent and high performance.
DAVID RIVAS: We're headed towards clearly fully
fault-tolerant architectures, and more and more,
it's starting to seem like a 10-year time horizon
for something like that is well within the means of the doable.
We at Rigetti believe, however, it
is the iterations on the years that
are probably most important.
We firmly believe that a few hundred, or maybe
a thousand or two high performing
qubits made available to application and algorithm
developers could potentially produce results.
No machines are ever built unless it's constant iteration
with the tools that you have.
And what we're doing here is building the machines
that we have iteratively and then using them as best we can.

ELICA KYOSEVA: It is a pleasure to be here today
and to tell you how NVIDIA is pioneering
the future of quantum computing with AI supercomputing.
To start, I would like to clarify one thing.
NVIDIA is not building a quantum computer or any other type
of quantum hardware.
What NVIDIA is doing is building all accelerated quantum
supercomputers.
The way that this will work is that NVIDIA supercomputers
will integrate quantum computers as co-processors.
These quantum computers can have different qubit modalities
and be manufactured by different QPU providers.
NVIDIA's solution is actually de-risking the quantum industry
by being hardware agnostic because for us, it
doesn't matter who produces the quantum computer.
We work with everyone to integrate their solutions
with our quantum supercomputers.
So what are the challenges that quantum computing is facing?
All applications will be running part
of their workload on a classical supercomputers,
and only part of the problem will be
solved on quantum algorithms.
So we need better hybrid algorithms.
We need also better developer tools,
and we need workforce development
in order to lower the barrier of entry
to domain experts that need to integrate quantum
computing as part of their workloads
at the moment of solving industry applications.
We need also better error correction codes
and also implementing quantum error correction
that requires very low latency between the quantum hardware
and the classical hardware.
And we also need infrastructure enabling
the tight integration between QPUs
and classical supercomputers.
And NVIDIA's GPUs are able to solve all of those problems.
GPUs will be used for quantum computing
research and development.
These include application development, circuit design,
dynamical simulations of quantum hardware,
which will enable better construction and better hardware
design.
GPUs will be used also for running quantum computers,
and their role will be in the readout in the calibration
of quantum computers, in fixing and decoding
errors that are detected during the operations of that quantum
computers in modularity where we need to couple tightly
quantum computers with classical supercomputers
and also in scheduling the power consumption of quantum
computers.
Hybrid applications will be using GPUs and QPUs and NVIDIA's
CUDA-Q programming framework allows for seamless applications
programming, where what is needed to be run on the QPU
is seamlessly programmed there while the rest is run
on a classical supercomputer.
CUDA-Q is designed to be used by QPU vendors,
by enterprises, by academics, and by anyone else that
would like to learn how to program the quantum
supercomputers of the future.
CUDA-Q includes libraries, programming model, tools,
and infrastructure.
What we could use CUDA-Q for is simulation
where the back end of CUDA-Q uses cuquantum,
which is an accelerated simulation library of quantum
computers which can provide state vector and tensor network
simulations, and also we can use CUDA-Q to program
actual quantum hardware.
CUDA-Q is already very highly adopted in the industry,
and we already have over 150 quantum partners.
Over 90% of the largest quantum computing startups use CUDA-Q,
and over 75% of QPUs are integrating NVIDIA software.
15 out of the 17 largest quantum computing
frameworks are accelerated with CUDA-Q. NVIDIA quantum
and CUDA-Q are open source, and we work
with everyone in the industry.
We work with quantum hardware providers, with cloud service
providers, with research centers around the world,
with quantum software providers, systems builders, and also
quantum simulation frameworks.
Quantum computing is supposed to have a broad impact
across many industries.
These include chemistry, drug discovery and pharmaceuticals,
logistics, finance, physics, modeling materials,
nitrogen fixation, and AI and machine learning.
All of these have in common very hard computational problems
for which we have proved that quantum algorithms will
be able to provide a solution that
is not possible to be obtained with classical methods.
For example, I would like to highlight a recent supercomputer
based on NVIDIA's GPUs called Gefion, which was purchased
by the Novo Nordisk Foundation to do research
in quantum computing for health applications
and to use the latest AI supercomputing
approaches to solve these problems.
We believe that accelerating everyone's solutions
is what is required in order to enable the future quantum
computing revolution and to realize the quantum
supercomputers of the future.

YONATAN COHEN: There was a time when
using machines to perform complex calculations
was a revolutionary idea.
Fast forward to today, controlling billions
of classical bits has become second nature, integrated
into every processor and computer,
affecting every bit of our life.
But now, with the emerging technology of quantum computing,
we're basically back to square one.
Quantum bits, or qubits, which are the quantum
counterparts of classical bits, are a whole new challenge.
They're delicate, they're error prone,
yet they're capable of astonishing computational power.
However, we live in the classical world,
so none of this quantum computation
would be possible without creating an interface that
transforms classical information to quantum operations and vice
versa.
And this is precisely the role of the quantum control system.
It's a set of tools that interact with quantum objects
and make information processing benefit from the wonders
of quantum mechanics.
To appreciate the crucial role of quantum control,
let's briefly examine the quantum computing stack.
At the foundation level, we have the quantum processing unit,
the QPU.
This is where the qubits reside.
Above this in the stack, we find the control and readout systems,
which manipulate and measure the qubits.
They do this by sending and receiving
a sequence of very accurate electromagnetic signals.
Next, we have the control software and firmware
translating high-level instructions
into qubit operations at the control pulses level.
At the top of the stack, we have, of course, the application
layer, where quantum algorithms are developed and run.
So quantum control, our focus today,
acts as the critical bridge between the classical and
quantum worlds.
It translates abstract quantum algorithms
into the precise physical operations
that manipulate the qubits.
MICHAELA EICHINGER: Controlling qubits is incredibly delicate,
like writing on a soap bubble without popping it.
To ensure qubits operate correctly,
we must generate precise and carefully timed
electromagnetic pulses.
Even the tiniest error in these pulses
can cause the qubit to end up in the wrong state,
derailing the entire computation.
Our control system is like the orchestra playing
music to the qubits, which dance in response.
Each pulse is a musical note, carefully composed
to guide the qubits' movements.
So how do we manage this composition?
A quantum controller acts like the conductor
of this intricate quantum orchestra.
It's a classical processing machine
responsible for generating and managing the control
signals that make qubits dance.
Key functions of such a controller are--
it generates precise pulses to manipulate qubits,
it reads out qubit states after operations,
it synchronizes all quantum operations,
it processes data and performs calculations in real time,
and it makes split second decisions,
adapting the control flow as needed.
YONATAN COHEN: At quantum machines,
we've pioneered a new approach to quantum control
with our pulse processing unit, the PPU.
So traditional systems, memory-based systems,
are like pre-recorded music.
They're limited to fixed sequences that take very long
to communicate with the control system,
and also cannot respond to what's happening in the quantum
processor in real time.
We moved from memory-based control system
to a processor-based one.
Our pulse processing unit, it's kind of like a live conductor
capable of making real-time decisions and corrections
on the fly.
This is crucial if you want your quantum program
to really respond to what's actually
happening with your qubits.
Moreover, we embedded classical compute engines inside our pulse
processing unit.
So now you can interleave quantum and classical operations
in the same code and then run them from the same hardware.
As the field progresses, the realization
that every quantum program is actually
a hybrid quantum classical program
strengthens and strengthens.
And so such tight integration between quantum and classical
becomes crucial.
This technology powers our OPX system, a comprehensive control
and measurement solution for quantum processors,
which embodies our vision of tight quantum
classical integration.
The PPU's multi-core architecture
allows for parallel signal generation, acquisition,
and processing, enabling the OPX to manage complex quantum tasks
at very high scales with unparalleled speeds
and precision on many, many, many qubits.
MICHAELA EICHINGER: Calibration is
one of the biggest challenges in quantum computing.
Consider the 2 qubit gate, a fundamental operation
in quantum computing.
In traditional systems, this can take a long time to calibrate,
and this calibration process has to be repeated for many qubits,
ending up in a process that takes hours.
Our OPX system can perform embedded calibration protocols
that significantly reduce this time.
We've seen QPU calibrations reduce from 8 hours
to just 30 minutes, and we expect
this to be reduced further to a matter of seconds.
Beyond calibration, quantum error correction
is crucial for enabling longer, more complex quantum
computations.
Yet the sheer amount of data processing
required for this is staggering.
To meet this challenge, we've partnered with NVIDIA.
We're combining our pulse processing units
real-time capabilities with GPU parallel processing connected
by an ultra low-latency interface.
This integrated system tackles the intense computational
demands of large-scale quantum error correction,
and with this, leads the way for powerful quantum
computers and a seamless quantum classical interface.
YONATAN COHEN: As we look to the future,
the challenges lie in scaling up quantum systems
from tens and hundreds of qubits to thousands
and tens of thousands of qubits, and beyond.
Our technology is designed with this future in mind,
providing the flexible and powerful control
necessary to manage such large-scale quantum systems.
The impact of our work goes beyond scaling.
We're opening new possibilities for
efficient hybrid quantum classical algorithms
and workflows.
This tight integration creates the fluid interface
between two powerful and complementary platforms--
the quantum processing unit, the QPU,
and the classical computing layer,
which is really the entire data center, boosting performance
to an uncharted and exciting regime.
In conclusion, at Quantum Machines,
we're building more than just control systems.
We're creating the vital link that
will allow quantum computers to reach their full potential.
Our technology is at the forefront
of bridging the gap between classical and quantum computing,
driving the next generation of computational breakthroughs.


ERIC HOLLAND: Welcome.
I'm Dr. Eric Holland, the General Manager
for Keysight's quantum engineering solutions group.
You may not be familiar with Keysight,
but likely you are with the company we spun out from,
Hewlett-Packard.
More than 80 years ago, Bill and Dave
used their engineering skills to design a product that
would help our first customer and Walt Disney Studios
not only record Fantasia in stereo sound,
but also be the first movie studio ever
to roll out stereo sound nationwide in movie theaters.
At Keysight, we are not building our own quantum computer,
and we haven't married ourselves to any one quantum technology.
The core of our company is design, test, and validation.
So by circumstance, our capabilities naturally
gravitated towards manufactured quantum technologies
such as superconducting qubits, spin qubits, quantum dots,
or photonic quantum processors.
So how do we fit in?
On the design side, we have software tools
to lay out and simulate the performance of quantum
processors and quantum limited amplifiers.
For test, we provide room temperature and cryogenic wafer
test and probing tools that are popular with foundries
and semiconductor organizations.
We also have network analysis tools
to understand cryogenic calibration and anomalous two
level systems.
On the validation side, we provide a wide array
of telecom products that are attractive to photonic quantum
processors, such as lasers and optical power attenuators,
while for superconducting and spin qubits,
we provide the quantum to classical interface,
the room temperature control electronics,
and quantum operating system.
We are agnostic on the first quantum computing
application for business.
Honestly, we're rooting across the board for quantum advantage,
because when the field wins, we win.
We do not expect to be the ones with the idea
for some novel algorithmic implementation that massively
changes how material design is approached in HPC.
Our goal is to provide the tools so that scientists and engineers
can focus on pursuing quantum advantage.
All quantum technologies have major hurdles
that they must overcome to implement a fault tolerant
quantum computer.
We believe that across the board,
the major challenges that must be addressed
are first, performance.
High fidelity single and multi qubit gates,
as well as develop robust real time protocols
to navigate noise.
Second, speed.
The wall clock time of the quantum computer
must be fast enough to address change
the world applications on timescales
relevant to industry applications.
The algorithm execution timescales cannot take decades,
centuries, nor millennia.
Third, scale.
A quantum computer implementing change the world applications
likely will have hundreds of thousands or millions
of physical qubits.
Great advancements in manufacturing
at scale for quantum processors must
be made across the entire supply chain, as well
as the miniaturization of key components
from a system design perspective so that the quantum computer is
of a manageable size as well as easy
to maintain for high uptime.
This is essentially swap C for quantum computing.
We hope that by and large, quantum computers
contribute to the good of humanity
as well as substantially advance our scientific knowledge.
We intend to contribute to the democratization of quantum
computing by providing software tools such as device design
simulation, as well as consistently improving
the quantum to classical interfaces
to foster a global community of quantum innovation.
Our hope is that by lowering the bar
to innovation, everyone benefits, not just a select few.
To date, the major vertical industries
integrating our quantum computing tools
are in the advanced computing domain.
Whether they are hyperscalers, high performance computing,
or systems integrators for end customers
such as national laboratories or general government.
We also support university efforts,
but their aim is typically different.
Either they are focused on the fundamental primitives
of the three major technological hurdles
and/or workforce development for the next generation
of scientists and engineers.
In addition, we have other aspects
we would like to include, which you might want to contribute to,
including quantum to classical interface,
classical electronics that control quantum computers,
software stack.
The quantum to classical interface
is where the rubber meets the road
in quantum computing, and all the engineering implementation
details matter.
The entire quantum to classical system
must enact the faithful and reliable execution
of quantum circuits, which are compiled down
into instruction sets for the underlying physical hardware.
Each quantum technology has its own unique requirements
for the quantum to classical interface.
Also, in every quantum to classical converter,
there are FPGAs that provide real time digital signal
processing on the output, input, or both.
Finally, the way in which all of this instrumentation in FPGA IP
is orchestrated together to enact quantum operations
is specific to the underlying quantum technology
it is interfacing with.
The quantum to classical interface
is a fantastic systems integration and systems design
problem for the coming decades.
If you look at the history of high performance computing,
the decades of the '70s, '80s, and '90s were dominated by major
architectural paradigms that enabled the next breakthrough.
We have made great progress in the last five years
on the quantum to classical interface,
but it is still very much in its early infancy.
No one at present has developed a platform
that can be trivially expanded from a SWOPSI perspective
to serve as the front end to a fault tolerant quantum
computer demonstrating quantum advantage.
As the field progresses forward, I
expect more ASICs to be developed specifically
to facilitate the quantum to classical interface.
My general expectation for the quantum to classical interface
is for it to become a larger engineering effort
over the next 5 to 10 years.
That will facilitate a transition from generalized
to specialized knowledge with cultivated expertise
in this area, and consequently for it
to become a long term career field.
As a quantum leader inside a large company or institution,
it is best to recognize that part of your role
is to provide the vision for how and why quantum fits in.
In one sense, the business challenges
Keysight faced when deciding whether or not
to enter quantum computing are typical of what one might expect
of any well-established company considering entering
into quantum computing.
Few, if any, large companies inherently
have quantum technologies as something
that was core to their company's previous success.
Typical questions and concerns from the executive team as well
as the shareholders are, does this make sense for our company?
Is this something we can make meaningful contributions to?
Why us and not someone else?
What is our moat?
My experience has been that it is best
to acknowledge that quantum computing is still
in its infancy, and that we must make calculated risks based
on our underlying technology assumptions.
My concluding thought here is that before technology arrives,
there is uncertainty on its future success.
Being at a company like Keysight that for 80 years
has been at the forefront of innovation,
we've accumulated a certain amount of risk tolerance
to the idea that the technology may arrive before the market is
ready, but our experience is that innovation rarely
goes to waste.


GUY SELLA: Classiq's approach is to provide
a full end-to-end quantum journey
by providing a software that can automate the entire development
process from modeling to execution.
This is a critical component for businesses venturing
into the world of quantum computing,
as the platform has its own high abstraction quantum programming
language that can be used on at least most of the quantum
computers exist in the market.
It is called Qmod.
And users can choose to use that or Python to do
the modeling with Classiq.
AMIR NAVEH: Quantum technology has rapidly
advanced in recent years.
It has become increasingly evident
that businesses require robust tools to leverage its potential.
At Classiq, we recognized that quantum software
plays a foundational role in this process.
Quantum and classical programming
are fundamentally different.
Developing and optimizing quantum algorithms
is inherently complex and requires a deep understanding
of quantum mechanics.
LIOR GAZIT: Development for quantum computers,
unlike development for classical computers,
requires understanding of the properties of hardware
that the code can be executed on,
as well as understanding the fundamental quantum principles,
such as superposition entanglement, and interference.
Quantum circuits are the quantum code
that is executed on a quantum computer.
It is made of quantum gates, similar to the electronic logic
gates.
And the quantum developer has to build the circuits for the code
to work on a quantum computer.
This can be done manually or automatically
by platforms like Classiq.
The circuits must be suitable for specific hardware.
Whether they are based on superconducting materials,
trapped ions, cold atoms, or photonic quantum computers,
each technology works with a different set of quantum gates
and has a different set of qubits, entanglement,
and topology.
The fact that such software is available
will make it easier for algorithmic developers
to think about the what and not about the how.
GUY SELLA: It is crucial to build a circuit
with the right characteristics.
Knowing them in advance makes it seamless
for Classiq to optimize the quantum circuits it generates.
LIOR GAZIT: Since most industries
aren't filled with quantum physicists or experts
in quantum information theory, it
is where high-level quantum software comes into play.
It abstracts away much of the complexity,
enabling users to leverage quantum computing
without needing to dive into the deep technical details.
GUY SELLA: In the short term, in what we call the NISQ era, Noisy
Intermediate-Scale Quantum, high-abstraction,
quantum software enables researchers and engineers
to start experimenting with quantum computing today.
Think about logistics companies looking
to optimize the supply chain.
With high-abstraction quantum software,
a seasoned development team can design and run
quantum algorithms to find optimal routes,
reduce costs, and increase efficiency, all without needing
to understand the underlying quantum circuits
or qubit manipulations.
LIOR GAZIT: The short-term advantage is crucial.
It allows industries to rapidly prototype quantum applications,
test different scenarios, and gain insights
that can translate into immediate operational
improvements.
Early adoption can also offer a competitive advantage,
helping businesses stand out as industry innovators.
As quantum hardware continues to evolve,
so will the capabilities of quantum algorithms.
Debugging of quantum algorithms is
something that doesn't exist today,
due to the technical difficulties mentioned
in this video.
But it will become reality soon.
Abstraction of quantum programming language
is designed to scale with these advancements,
ensuring that projects can seamlessly integrate new quantum
technologies as they emerge.
GUY SELLA: I will say it cautiously with a pinch of salt.
Most of the Fortune 500 companies
already started exploring the technology,
while some have already shown profound research
in a range of different topics.
The amount of governmental investment and grants injected
into the quantum market by the leading global governments,
such as the United States, the United Kingdom, Japan, Canada,
Italy, and other countries, demonstrate
that quantum is a strategic asset for nations.
This fuels the growth of the quantum market.
AMIR NAVEH: The same applies to AI.
Quantum neural networks have the potential
to accelerate and scale a broad range of algorithmic solutions
for otherwise intractable problems.
They can effectively approximate functions
by exploring diverse functional spaces,
leveraging their unique topological structures.
By operating within these complex landscapes,
quantum neural networks can capture intricate patterns
and correlations, enhancing the expressiveness
of the approximation.
Quantum neural networks offer interpretability,
which is particularly valuable in scientific computing.
Scientific computing is a driving force
behind numerous industries where advanced modeling and data
analysis drive success.
Several multibillion dollar industries in the US alone--
for example pharmaceuticals and biotechnology,
where it accelerates drug discovery,
molecular modeling and genomics.
The financial industry leverages scientific computing
for quantitative analysis, risk modeling,
and high-frequency trading.
In aerospace and automotive sectors,
it supports computational fluid dynamics, structural analysis,
and design optimization.
The energy industry, including oil and gas exploration
and renewable energy.
Lastly, in health care, it enhances medical imaging,
diagnostics, and personalized medicine,
improving patient care and outcomes.
These domains, powered by scientific computing,
are among the most transformative
in the global economy.
The enhanced interpretability offered by quantum neural
networks and quantum optimization algorithms
is particularly impactful in these sectors, where
understanding complex models and deriving accurate solutions
is crucial.

Reaching the fault-tolerant era of quantum computing
is expected to take time, likely within the next decade,
as quantum systems gradually achieve
sufficient computational volume and robust error correction
capabilities.
GUY SELLA: A big challenge that Classiq is facing
is the simple fact that the global quantum market
is a small, emerging market.
It's true that companies know they need
to start working with quantum.
But there are no substantial business applications
in production yet, apart from research, mainly
because of the current hardware limitations.
Today, advanced technologies that are already in production,
such as generative AI and blockchain
get more attention because they can produce faster.
I would say that market adoption is another challenge
that we are facing.
The market is small but competitive.
And as a small and ambitious startup,
we need to shine to get the attention of the major quantum
engineers and researchers who already work
with other technologies to hear about Classiq
and, over time, to prefer it over their existing
technologies.
Gladly, we are gradually hitting our goals
towards much wider adoption-- academia,
private, and public sectors.

AMIR NAVEH: Understanding quantum computing principles
and developing practical skills in this field
will be crucial for scientific and technology advancements.
By gaining expertise in quantum programming skills now,
you'll be well prepared to contribute to groundbreaking
research and potentially revolutionary applications
as quantum computers continue to evolve.
This knowledge will be invaluable
across various disciplines, from material science
to cryptography, positioning you at the forefront of emerging
technologies.
GUY SELLA: Classiq works with some of the leading companies
in the world in different domains--
major banks in the United States and Europe,
large automotive companies, several global telecommunication
enterprises, and companies in aerospace and defense,
chemistry, and manufacturing.
LIOR GAZIT: Businesses that adopt a software
that integrates with the major hardware providers in the market
enables hybrid solutions that combine classical and quantum
approach.
Hybrid solutions can better address complex business
challenges.
Quantum software that provides a high-abstraction programming
language is essential for organizations
looking to capitalize on quantum computing.
It lowers the entrance barrier to quantum,
allowing companies to start experimenting
with quantum solutions today.
GUY SELLA: A quantum software provides
a scalable platform that will grow business's quantum assets
and best practices as quantum technology evolves.
Those who embrace quantum software
now are not just preparing for the future.
They are actively shaping it.


We've talked about the promise of quantum computers
and their potential for quantum advantage.
Clearly, some problems are very hard to compute
on a classical computer, and for some of these problems
a quantum computer is much more efficient.
But what makes a problem hard in the first place?
You've probably heard of problems being categorized
as P or NP, NP-complete.
But what do these categories mean, and how
do computer scientists classify a problem as an easy problem
or a hard one?
In this deep dive, we'll hear from Professors Ike
Chuang and Peter Shor about the computational complexity
of classical computing, how it's defined,
and how problems are classified, including a discussion
of several standard problems that are classified as P,
and NP, and NP-complete.
Let me describe a little bit about universality
in the language of the circuit model of computation,
because that's what we naturally know best,
and also is what we will build quantum computation upon
as a language.
So in the circuit model, for example,
we may have AND gates and NOT gates.
And I want to claim that all Boolean circuits, circuits
that compute Boolean functions, can be composed of AND and NOT.
And this is fairly easy to see, but first
let's look at the family of Boolean functions.
They will be functions that take,
if there are n bits of input, say x0 to xn minus 1,
and the result of this is going to be either 0 or 1.
OK, so for example, in the notation
I will say that we may have f of x1x2 be x1x2.
And this product represents an AND gate.
Or for example, f of x is equal to x-bar.
And this is how I will represent a NOT gate.
OK?
Now, the question of universality
dovetails with another question.
And I haven't finished the universality description yet,
but I want you to keep this in mind of complexity,
because it's not terribly useful if I say something
about universality without saying how much cost it
takes to accomplish something.
So here, the key idea which we will not have time
to go into much depth on, but I hope you already
know something about, which is that some math problems are
harder than others, apparently.
And I don't mean it's hard to multiply
two million-digit numbers, and that's harder than multiplying
two 10-digit numbers.
No, that's not the point.
The point is they're scaling with respect
to the size of the problem.
And this leads to a statement which I hope that all of you
already know of in some form, which
is called the Strong Church-Turing Thesis.
And I'll write this up for you, because I
think the words of this are very useful in understanding
the perspective.
So we say, any model of computation
can be simulated on a specific kind of machine.
And the machine and model I would choose
will be this one here, the Turing machine.
But I'm going to choose a specific variant of it,
the probabilistic Turing machine.
And I need to say something about the cost
of this kind of simulation.
And the essence of that thesis is that this simulation cost
comes with, at most, a polynomial increase
in the number of elementary operations required.
It's an extraordinary thesis.
It defines an equivalence between models, whether they
be electrical and optical or electrical and DNA or quantum
and DNA or quantum and classical.
And for even that to be possible conceptually is remarkable.
And I haven't defined a lot of the technical terms
in this, like simulation and the overhead costs,
but I hope you'll get to appreciate that as we go along.
OK.
So now, in order to highlight this statement of equivalence,
let me make sure you are aware of one of the greatest
motivating factors for quantum computing, which
is the difference between two of the most important classes
of mathematical problems.
And for this, I'll use this fact that many problems can be
expressed as decision problems.
So for example, is the number M prime?
And the answer to this is yes or no.
Is this a hard problem or an easy problem?
This actually was not known for many years.
It was then realized that you could answer this question
with some randomness.
You wouldn't know it for certain.
This is Rabin's primality testing algorithm.
And then some 15 years ago, somebody in India
proved that you could do it deterministically.
So it moved from this probabilistic model,
which people had to use previously for this question,
to something which did not need probability.
So today, there is a deterministic primality testing
algorithm.
And this problem is called primality.
OK, so that's one example.
Here's another one.
It's called factoring.
Given a composite integer m, but not
just the number that we're going to try to factor, also
and a number l, an integer l, which is less than m,
does m have a factor that's non-trivial
which is less than l?
So we need to bound the sides of the range of numbers
we're going to consider as being answers to the problem.
And again, this is a yes or no question.
And we have this distinction.
If the time taken to answer this question,
needed to answer this question, is
polynomial in the size of the question--
and here, for example, for factoring,
this is the number of bits of m, the number of digits
in the number, OK-- it's not just the number itself--
then we say that the problem is polynomial in complexity.
So we say it's in this class that we'll call P.
Now, let me break down the class of whether this is something
answered by a yes or by a no.

If the yes instances of the problem are easily checked--
and I'll use the word verified as a technical term--
with the aid of a witness, which is a short description
piece of information that enables
somebody else who's not terribly skilled
at the arts but can be very reliable,
to verify your claim.
Sometimes, we talk about a Merlin and an Arthur.
We say that the Merlin is somebody who's very clever
and can come up with proofs, but you
need the Arthur, who is not terribly clever
but can be very, very reliable to take that proof
and verify the claim.
So there are two parties to this, the verifier
and the prover.
And the verifier takes this witness.
Then we say, if this is true, then the problem,
even if it is very difficult, the fact
that we can verify the proof of it
means that we will say that the problem is
in this class called NP.
And in some senses, I want to say this is non-polynomial,
but the main point of this is the distinction
between P and NP.
And for sake of completeness, we have another parallel to this,
which is the mirror image.
If no instances-- so this is the answer is yes,
and this is the answer is no--
with exactly the same language, then we
say that the problem is in a different class called co-NP.

And I do this not because I want to say anything
more about P versus Co-NP or NP versus Co-NP,
but just to share with you a trivial fact in a moment.

So the reason I show this is because so
much of the motivation for computation today,
and much of quantum computation comes from this question of NP
versus P. We think that the P problems are easy
and the NP problems are the hard ones and meaningful ones to do.
And there's this plot that you can
make which shows that, if this is
the space of all mathematical problems,
then P is a subset of something we might say is NP,
but there's also this extra area over here, which is
the hardest of the NP problems.
And we call these the NP-complete problems.
And they're defined as such because,
if you can solve any of the problems that are NP-complete,
then it gives you a polynomial time algorithm
to solve any of the other problems in the NP regime.
So where's quantum computation in all of this map?
Well, I'm not going to answer that for you today,
but I hope that, through the course
of this class and this semester, you'll
start to appreciate where quantum computation is
relative to this landscape of the field of all problems
and their complexities.
Quantum computation sits kind of differently in this landscape.
It has a complexity class, typically of something
we call BQP.
And part of the reason for that is
because the model is slightly different, and doesn't
fit directly into either of these classes,
because sometimes the output is quantum mechanical.
There are errors involved, and some things
we'll come to later.
Good.
So I hope many of you already knew about most of this,
but I also hope that it starts to connect some things for you.
An example of an NP-complete problem--
and now I'm going to go back to the concept of universality--
is-- so an example is a problem called 3-SAT.
And this is about the satisfiability
of Boolean functions, which looks something like this.
So suppose you have, again, a function of bits
x0 through xn minus 1.
And the formulas that are involved in 3-SAT look
something like x1 plus x3 plus x9, OR’d together,
AND’d with--
there's a multiplication here--
another term, like x4 plus x7-bar plus x11,
and so forth and so on, where each one of these terms just
has three bits, and your goal is to say,
does there exist an assignment of zeros and ones
to the x inputs such that the output is equal to 1?
Seems very simple.
It's very easy to write this problem on the board.
But if you can solve this problem fast in time
that’s polynomial with n here, then
it turns out you can solve all the rest of these problems
fast.
And in fact, if you can solve this problem fast,
you can solve problems like the optimal way
to pack boxes into a FedEx truck,
or the optimal way to route a packet in for information
from San Francisco to Boston.
You know, it's really remarkable how powerful
such a simple problem can be.
And yet, I can show that, in practice, you can't really
solve most of the instances of this problem
as well as we would like to.
Yes, please.
Are there simple problems that are neither P nor NP?
Are there simple problems that are neither P nor NP?
Yes.
Another interesting class that sits outside of this
is the class of counting the number of solutions
to a problem.
That's the class called sharp-P. And so on and so forth,
because you might count the number of things to count
the number--
OK.
But you know, this is how you get
a career as a theoretical computer scientist.
It's very effective.


So what is complexity theory?
Theoretical computer scientists love to come up
with complexity classes.
So P is polynomial time computation.
NP, things you can prove in polynomial time.
So who here doesn't really know about NP?
OK, so let's explain NP a little bit.
The most famous NP complete problem
may be the traveling salesman problem.
And here you have a graph, distances
between, let's call them, cities, which are really
the nodes of the graph.
And the question, is there a path visiting all cities
less than length l?

So this might be 1, 2, 3, 5--
or no 2, 3, 1, 1, 2, 3.
So this would be a path of length 12.
And of course, there are distances--
I mean there are roads between the cities I haven't put on
here at distances along those roads,
if these were the only roads, it would be an easy problem.
And in fact, if there's only six vertices, it's an easy problem.
So it's easy to prove yes.
So if I want to prove that there's a path,
I just give you the path, and you
add up the distances along it and check it.
And I can prove it.
But it's hard-- or may be hard to prove no.
So how can I prove that there is no path shorter
than distance 12 on that route?
Well, I could run through all paths
and check all their distances but that
takes a very long time.

And if I know and if I were trying to convince you
that I've done this, would there be a better way
to convince you other than just say, well, I
ran through all the paths and checked them?
And actually, for the traveling salesman problem
there are better ways but they all
seem to be exponential time in the worst case.
Or exponential time in the number of cities.
And now there are problems that are NP-Complete,
which are as hard as any NP problem.
In other words, if I could solve an NP-Complete problem
in polynomial time in the length of its input,
I could solve any problem in NP in polynomial time
the length of its input.

And you do that by reducing one problem to another.
And at some point in the 1990s, I think,
computer scientists came up with interactive proofs.
And there are three classes of interactive proofs.
IP, no bound on the number of rounds,
AM, and here “A” stands for Arthur and “M” stands for Merlin.
And Merlin has infinite computing power
and Arthur really only has polynomial amount
of computing power.
So A sends M message, M returns message.
So that's two rounds.

And then there's also MA.

M gives A proof.
A verifies it with coin flips.
So NP, Merlin gives Arthur a proof and Arthur
verifies it deterministically.
MA, Merlin gives Arthur a proof and Arthur verifies it,
but probabilistically.
And AM, Arthur sends Merlin a message,
and Merlin returns a message.
And the classic example of AM is graph non-isomorphism.
Are these two graphs isomorphic, and NP.
so we're given two graphs and I guess these have 5, 6, 1, 2, 3,
4, 5, 6.

So the question is, is there a way to relabel the vertices
so that they are the same?
And the guess answer is an NP, isomorphism is in NP.
Merlin just gives Arthur a relabelling.
So Merlin says 1 in this graph corresponds to 5 in this graph.
3 in this graph corresponds to 4 in this graph, et cetera.

OK.
And non-isomorphism is an AM.

Arthur takes one of the graphs.
He re-numbers the vertices at random
and he sends it to Merlin.
And Merlin is supposed to--
Merlin says which graph it is.
Now, if the two graphs are isomorphic,
you know, Merlin has the scrambled graph
but a random scrambling of this graph
looks exactly like a random scrambling of this graph.
So he can't tell them apart.
And if the two graphs are not isomorphic,
then if Merlin has an infinitely powerful computer,
he can try all possible permutations
and tell them apart.
So that says that non-isomorphism
is an Arthur-Merlin.
