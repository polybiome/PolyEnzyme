<h2>QUICK START</h2>

To run the code you will need python 3.4 + kivy 1.9.1 + numpy + matplotlib. Alternativelly if you're on windows you can just download and run our executable by downloading PolyBiome.rar


<header style=" margin: 0 30px;color:#5B8DDA">
**POLYENZYME - DOCUMENTATION**
============
</header>
<main id = "main">
<h2>1. Introduction</h2>
<p>
PolyEnzyme is an interactive enzymatic pathway simulator, with a focus on intuitiveness, graphic visualization, and ease of use. It is part of the software entrance of the team UPF-CRG Barcelona, for the international synthetic biology competition iGem 2016.
</p>
<h4>1.1 Overview</h4>
<p>
The program consists on a blank canvas on which nodes can be placed. Those nodes represent reaction components, such as inhibitors, substrates and products. Once a set of nodes is present on the canvas, the user can link them in enzymatic reactions. The simulation can then be run in real time or for a desired time, whereupon the nodes will update their properties graphically following the specified reactions.

Additional functionality consists on the user being able to save the created pathways for latter use and revision. It is also possible to choose and download a pathway from examples in the web.


</p>
<h4>1.2 Scope</h4>
<p>
PolyEnzyme was originally designed to check and compare the validity of experimental data in the Barcelona 2016 iGem team project. Although the focus latter shifted to generalize the program and make it more suitable to learning and academic purposes, it is well capable of performing predictions for comparing experimental data, and of obtaining the general behavior of diverse pathways. 

It is however imperative to understand the limitations of the software and the basic details of the algorithms implemented, in order to ensure the validity of the equations against the real enzymatic and genetic processes happening inside the cell. PolyEnzyme is provided **without any guarantee**, and its predictions, even when the computation is performed inside the range of validity of the equations, are only indicative of the real chemical processes underlying the pathways.
</p>

<h4>1.3 Fair use and sharing</h4>
<p>
PolyEnzyme is provided under the MIT license</p><a>https://opensource.org/licenses/MIT</a>


<h2>2. Structure of the program</h2>

</p>
<h4>2.1 Nodes</h4>
<p>

The nodes represent the compounds in the enzymatic reactions, whether products, substrates or inhibitors. They possess a name, a concentration and can be set as sink/sources. When in this mode, the concentration is no longer set; the node can yield infinite amounts of mass when set as a source, and receive  infinite amounts of mass when set as a product. For more information about this behavior refer to the reactions section.

To start creating nodes, the user can click at a void spot inside the canvas. A prompt will then appear asking for the basic information of the node. If no information is set, the defaults (blank name and concentration = 1[mM]) will be defaulted.

Once created, the user can move the node around the canvas by clicking and dragging on its sprite. Double-clicking the node will allow for re-specifying the node's parameters.
</p>
<h4>2.2 Reactions</h4>
<p>
Reactions represent the enzymatic reactions in the pathways. A reaction links a set of substrates with a set of products, and can be inhibited by a set of inhibitors. Reactions are treated independently of the nodes, and follow Michaelis Menten kinetics. 

The basic Michaelis Menten formulation is an aproximation on enzymatic reactions of the type:

    S + E <-> SE -> P + E

Where S is a substract, P is a product and E is an enzyme. The rate of the equation is modelled mathematically as:

    v0 = [S]Vmax/(k + [S])

Where Vmax and k are constants given by the reaction characteristics, and can be gatered from web services such as Brenda or Kegg.

The substract and products are updated depending on the equation rate, in the following manner:

    dP/dt = v0

    dS/dt = -v0

Which guarantees mass conservation inside the system (if no sink/source nodes are present in the pathway).

To create a reaction in PolyEnzyme first there has to be two or more nodes in the canvas. Pressing the button "Create reaction" in the top left menu initiates the reaction wizard. This has two functions:
</p>
<h5>2.2.1 Create Reaction</h5>
<p>
This process has two phases. First, all the nodes acting as sources must be selected (they become highlighted in green). Once this is done, click "Done" in the top left menu to start the second phase, where the products are selected (highlighted in blue). Note that a node can't be product and source of the same reaction. When all the products are selected, cliking again the "Done" button will trigger a prompt asking for the enzyme catalyzing the reaction (optional) and the parameters Vmax, km. Not setting those parameters will result in them initializing at 1.5[mM/s] and 0.5[mM] respectively.
</p>

<h5>2.2.2 Set inhibition</h5>
<p>
If the reaction is gonna be a inhibition on an existing reaction, the selected source nodes will represent the inhbitiors of such reaction. To create the inibition, click on any reaction in the canvas. A prompt will appear asking for the inhibition type and the inhibition constant Ki. The inhibition type can be set to Competitive, Uncompetitive or Non-Competitive(mixed). 
</p>
<h6>2.2.2.1 Competitive Inhibition</h6>
<p>
Binds the complex EI + S, where I is the inhibitor. It only affects Km, and therefore has less effect at high substract concentrations. Here, ki is the actual EI complex dissociation constant.

	v0 = Vmax[S]/([S] + km(1+[I]/ki))
</p>
<h6>2.2.2.2 Un-competitive Inhibition</h6>
<p>
Binds to the complex ESI. It only affects Vmax, and therefore has less effect at low substract concentrations.

	v0 = Vmax[S]/([S](1+[I]/ki) + km)
</p>
<h6>2.2.2.3 Non-competitive (mixed) Inhibition</h6>
<p>
Binds to both, affecting Vmax and Km.

	v0 = Vmax[S]/([S](1+[I]/ki) + km(1+[I]/ki))

</p>
<h4>2.3 Solving</h4>
<p>
Once the user is satisified with the pathway, it can be solved by clicking to the "Solve" button on the bottom left of the screen. PolyEnzyme will integrate the equations defining the system with a 2n order Runge Kutta algorithm. The size of the differential, maximum time and resolution of the solution can be specified in the settings panel (see section 4). Depending on the setings and complexity of the pathway, computing the solution may take a few minutes. Once solved, the results will be displayed on a graphic showing the time evolution of the concentration for all nodes.
</p>
<h4>2.4 Real-time Solving</h4>
<p>
At the bottom left of the screen there is a horitzontal slider. Modifying its value will trigger a continuous update of the nodes in the canvas. This may be useful to visualize how the system behaves in a more intuitive way. The slider value modifies the velocity at which the solution subrutine is trigered. Not that the maximum velocity may depend on the system specifications of the user.
</p>

<h2>3. Other utilities</h2>
<h4>3.1 Saving and loading</h4>
<p>
The saving and loading functionalities allow the user to store pathways for future use, reload them into the application, and obtain pathways from the repository. Clicking the save button on the left side panel triggers a prompt asking for the schematic name. The system is saved in json format in /saved, where PolyEnzyme.exe is located. Clicking the load button down below opens a prompt that allows the user to select all existing saved pathways in the /saved folder, and a selections of different pathways located in the repository.
</p>
<h4>3.2 Erasing mode</h4>
<p>
 By clicking the button with the same name on the left side panel the user enters in delete mode. In this mode, reactions and nodes can be removed by clicking on them. Note that deleting a node will erase all its associated reactions.
</p>
<h4>3.3 Erasing everything</h4>
<p>
Clicking the button by the same name in the left side panel will remove all nodes and reactions, yielding a blank canvas to work with.
</p>
<h2>4. The settings panel</h2>
<p>
Clicking the settings button on the left side will open the settings panel. The settings panel gives access to the user to the following variables:
</p>
<h3>4.1. T Max</h3>
<p>
This controls for how many seconds will the solution be computed when cliking "Solve". It is independent of the solution resolution (dt).
</p>
<h3>4.1. dt</h3>
<p>
This controls how acurate is the Runge Kutta algorithm. A smaller integration step represents less aproximation in integrating the system. For most applications, a step of 0.1 should suffice. 
</p>
</main>






