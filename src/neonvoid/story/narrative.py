"""Narrative text for all story beats triggered by events."""

from __future__ import annotations


NARRATIVES: dict[str, str] = {
    # ═══════════════════════════════════
    # ACT 1: "WHO AM I?"
    # ═══════════════════════════════════

    "act1_readme": (
        "The screen flickers. These words were left for you -- by you? "
        "By someone who knew you'd be sitting here, disoriented, with nothing "
        "but a blinking cursor and a headache that feels like static.\n\n"
        "[dim italic]Something happened. And this terminal is your only thread.[/dim italic]"
    ),

    "act1_identity": (
        "Kai Voss. The name feels... almost right. Like wearing someone else's "
        "shoes that happen to fit. Employee of Omnicron Industries, assigned to "
        "the Nexus-7 facility. Welcome aboard.\n\n"
        "[dim italic]But why does none of this feel like a memory?[/dim italic]"
    ),

    "act1_urgent": (
        "The message is terse. Desperate. Whoever 'R' is, they were afraid. "
        "\"They know.\" Know what? And who are \"they\"?\n\n"
        "[dim italic]The sent folder might hold answers. And whatever was deleted...[/dim italic]"
    ),

    "act1_deleted_mail": (
        "Deleted but not destroyed. Whoever cleaned up after themselves was either "
        "careless or didn't have time to do it properly. The traces remain, like "
        "bloodstains under UV light.\n\n"
        "[dim italic]What else is hiding in plain sight?[/dim italic]"
    ),

    "act1_ssh_creds": (
        "Server coordinates. Access codes. Someone left you a lifeline to the "
        "corporate network. These credentials could open doors -- or seal your fate.\n\n"
        "[dim italic]There's a whole network out there beyond this terminal. "
        "What's Omnicron hiding behind its firewalls?[/dim italic]"
    ),

    "act1_grep_lethe": (
        "LETHE. The name surfaces again and again, like a body that won't stay "
        "submerged. It's in the logs, in the errors, in the corrupted memory sectors. "
        "Whatever LETHE is, it's deeply embedded in this system.\n\n"
        "[dim italic]In Greek mythology, Lethe was the river of forgetfulness. "
        "The dead drank from it to erase their memories of life.[/dim italic]"
    ),

    "act1_chmod_lethe": (
        "The file was locked down. Someone didn't want this read. But permissions "
        "are just numbers, and numbers can be changed.\n\n"
        "[dim italic]Now you can see what they were trying to hide.[/dim italic]"
    ),

    "act1_lethe_revealed": (
        "[bold yellow]PROJECT LETHE: Cognitive Restructuring Initiative[/bold yellow]\n\n"
        "Memory erasure. Neural reprogramming. They're not building a product -- "
        "they're building a tool to rewrite human minds. The clinical language "
        "can't disguise what this is: a weapon against consciousness itself.\n\n"
        "[dim italic]And you're locked in a room in the facility where they do this. "
        "That can't be a coincidence.[/dim italic]"
    ),

    "act1_network": (
        "Three servers on the internal network. Nexus-core: the corporate brain. "
        "Archive: deep storage. Lab-9: research facility. Each one a layer deeper "
        "into whatever Omnicron is really doing here.\n\n"
        "[dim italic]You have credentials for nexus-core. Time to go deeper.[/dim italic]"
    ),

    # ═══════════════════════════════════
    # ACT 2: "WHAT HAPPENED?"
    # ═══════════════════════════════════

    "act2_enter": (
        "The corporate mainframe stretches out before you like a digital city. "
        "HR records, financial data, internal communications -- the entire nervous "
        "system of Omnicron Industries, laid bare.\n\n"
        "[dim italic]Somewhere in this data is the truth about what happened to you. "
        "And what happened to 'R'.[/dim italic]"
    ),

    "act2_river_death": (
        "[bold red]River Chen. Status: DECEASED.[/bold red]\n\n"
        "'R' has a name now. River Chen, senior researcher, terminated for "
        "\"security breach.\" But terminated takes on a different meaning when "
        "the word next to your name is DECEASED.\n\n"
        "[dim italic]She tried to warn you. And they killed her for it.[/dim italic]"
    ),

    "act2_chat_logs": (
        "The chat logs paint a picture of a corporation rotting from the inside. "
        "River's warnings, dismissed. Her concerns, ignored. And then... silence. "
        "The day she stopped posting is the day she died.\n\n"
        "[dim italic]No one helped her. Or maybe no one could.[/dim italic]"
    ),

    "act2_private_msg": (
        "River's private messages to you. She trusted you. \"Don't believe what "
        "they tell you about the project. Don't believe what they tell you about "
        "yourself.\"\n\n"
        "Director Sable's messages are different. Warm. Encouraging. \"You're doing "
        "important work, Kai. The world needs Project LETHE.\"\n\n"
        "[dim italic]Two voices. Two versions of reality. Which one was lying?[/dim italic]"
    ),

    "act2_financial": (
        "Shell companies. Offshore accounts. Millions flowing through entities "
        "that exist only on paper. Project LETHE isn't just unethical -- it's "
        "built on a foundation of financial crime.\n\n"
        "[dim italic]They're funding illegal human experimentation with laundered money. "
        "This goes all the way to the top.[/dim italic]"
    ),

    "act2_cameras": (
        "[bold red]The camera footage freezes the blood.[/bold red]\n\n"
        "Floor 7, 02:14 AM: A figure matching your build enters the building. "
        "Lab 9, 02:47 AM: That same figure -- you -- is being wheeled on a "
        "gurney, unconscious, into a room marked 'PREPARATION.'\n\n"
        "[dim italic]You came here. Willingly? And then something happened "
        "that put you in that room with nothing but a terminal.[/dim italic]"
    ),

    "act2_voicemail": (
        "River's voice, transcribed but still somehow carrying the weight of "
        "desperation: \"Kai, it's River. I hid the proof in the archive. "
        "Everything Sable doesn't want the world to see. Find it. Please.\"\n\n"
        "[dim italic]A message from a dead woman. Her last act was to give you "
        "a fighting chance.[/dim italic]"
    ),

    "act2_firewall_hint": (
        "The firewall rules show it clearly: the archive server is deliberately "
        "blocked. Someone configured this firewall to keep the archive sealed. "
        "But every wall has a weakness.\n\n"
        "[dim italic]Examine the rules carefully. There might be a way to "
        "disable the block.[/dim italic]"
    ),

    # ═══════════════════════════════════
    # ACT 3: "WHAT AM I?"
    # ═══════════════════════════════════

    "act3_enter": (
        "The archive server hums with the weight of buried secrets. Everything "
        "Omnicron wants forgotten is stored here -- and a scheduled wipe job is "
        "counting down to erase it all.\n\n"
        "[dim italic]River died to protect what's in these files. "
        "Don't let it be for nothing.[/dim italic]"
    ),

    "act3_evidence_extracted": (
        "The compressed archive expands into a directory of damning evidence. "
        "Documents, transcripts, authorization forms signed by Director Sable. "
        "River assembled this like a prosecutor building a case.\n\n"
        "[dim italic]This is everything. The proof of what they've done. "
        "But the worst truth might be the one about you.[/dim italic]"
    ),

    "act3_subject_031": (
        "[bold red]═══════════════════════════════════════════════════[/bold red]\n"
        "[bold red]  SUBJECT 031: VOSS, KAI[/bold red]\n"
        "[bold red]  STATUS: VOLUNTEER[/bold red]\n"
        "[bold red]  PROCEDURE: FULL COGNITIVE OVERWRITE[/bold red]\n"
        "[bold red]═══════════════════════════════════════════════════[/bold red]\n\n"
        "You are Subject 031. Not an employee. A test subject. The \"Kai Voss\" "
        "identity -- your name, your memories, your entire sense of self -- was "
        "programmed into you. Written over whoever you used to be.\n\n"
        "[dim italic]The headache isn't from waking up. It's from the procedure "
        "that rewired your brain.[/dim italic]"
    ),

    "act3_true_identity": (
        "The original record tells a different story. Before you were Kai Voss, "
        "you were someone else. A journalist investigating Omnicron Industries. "
        "River Chen was your source. You came to expose them.\n\n"
        "And they turned you into one of their experiments.\n\n"
        "[dim italic]Everything you thought you knew about yourself is a "
        "fabrication. But the person you were -- that person was trying to "
        "do the right thing.[/dim italic]"
    ),

    "act3_backdoor": (
        "River's last gift. A hidden tunnel into Lab-9, the facility where "
        "they performed the procedure on you. Where they plan to finish the job.\n\n"
        "Her note is simple:\n"
        "\"[italic]Kai -- use this to get into the lab. The door controls are on the "
        "lab server. I'm sorry I couldn't get you out in time. Make it count. -River[/italic]\"\n\n"
        "[dim italic]She's gone. But she left you the keys.[/dim italic]"
    ),

    "act3_river_farewell": (
        "River's insurance policy. Written in case the worst happened -- and it did. "
        "\"If I go missing, check archive/classified. Everything is there. "
        "The subjects, the budget, the bodies. All of it.\"\n\n"
        "[dim italic]She knew they would kill her. And she made sure her death "
        "wouldn't bury the truth.[/dim italic]"
    ),

    # ═══════════════════════════════════
    # ACT 4: "HOW DO I GET OUT?"
    # ═══════════════════════════════════

    "act4_enter": (
        "Lab-9. The place where memories die and new ones are born. The server "
        "controlling this facility -- controlling your room, your door, your "
        "very observation -- is now at your fingertips.\n\n"
        "[bold red]This is where it ends. One way or another.[/bold red]"
    ),

    "act4_surveillance": (
        "The camera feed describes a person sitting at a terminal in Room 31. "
        "Heart rate elevated. Brain activity: anomalous. \"Subject is accessing "
        "restricted systems. Alert level: CRITICAL.\"\n\n"
        "That person is you. They're watching you right now.\n\n"
        "[dim italic]The observation goes both ways now.[/dim italic]"
    ),

    "act4_schedule": (
        "[bold red]Subject 031 -- FULL COGNITIVE WIPE -- 0600 TOMORROW[/bold red]\n\n"
        "Not a partial erasure. Not a restructuring. A complete wipe. "
        "Everything that remains of who you were -- the fragments, the doubts, "
        "the faint sense that something is wrong -- all of it will be erased. "
        "Permanently.\n\n"
        "[bold yellow]You need to get out. Now.[/bold yellow]"
    ),

    # ═══════════════════════════════════
    # DOOR UNLOCK
    # ═══════════════════════════════════

    "door_unlocked": (
        "[bold green]╔════════════════════════════════════════╗[/bold green]\n"
        "[bold green]║        DOOR LOCK DISENGAGED            ║[/bold green]\n"
        "[bold green]║        ROOM 31: UNLOCKED               ║[/bold green]\n"
        "[bold green]╚════════════════════════════════════════╝[/bold green]\n\n"
        "The magnetic lock releases with a heavy clunk. For the first time "
        "since you woke up, there's a way out of this room.\n\n"
        "But before you go... the evidence. River's evidence. Everything she "
        "died for, everything that proves what Omnicron has done.\n\n"
        "The communications relay in escape/comms/ can send it out. "
        "To a journalist. To the authorities. To everyone.\n\n"
        "[dim]Check escape/comms/contacts.txt for relay endpoints.\n"
        "Use: curl --data @EVIDENCE relay://<target>\n"
        "Or just type 'exit' to leave. The door is open.[/dim]"
    ),

    # ═══════════════════════════════════
    # ENDINGS
    # ═══════════════════════════════════

    "ending_a": (
        "The data streams out through the relay. Megabytes of evidence, "
        "compressed into a single burst -- financials, subject files, "
        "authorization documents, camera footage. All of it.\n\n"
        "An alarm sounds somewhere deep in the building. Red light seeps "
        "under the door. They know.\n\n"
        "But it's too late. The evidence is already gone, racing through "
        "fiber optic cables to a journalist who will know exactly what "
        "to do with it.\n\n"
        "You step through the door.\n\n"
        "The corridor is empty. Emergency lighting casts everything in "
        "crimson. You follow the exit signs -- muscle memory from a life "
        "you can barely remember -- down a stairwell, through a loading "
        "dock, and out.\n\n"
        "Rain. The shock of cold air. Neon reflects off wet asphalt in "
        "colors that feel impossibly vivid after the sterile white of "
        "Room 31.\n\n"
        "You are free. And somewhere, the truth is being read.\n\n"
        "In the weeks that follow, Omnicron Industries makes headlines "
        "for all the wrong reasons. Director Sable vanishes. The lab is "
        "raided. Fourteen former subjects are identified and located.\n\n"
        "You stand in a city that looks both familiar and foreign, with "
        "a name that isn't yours and memories you can't fully trust. "
        "But you are alive. And the right thing was done.\n\n"
        "[bold]River would have wanted it this way.[/bold]"
    ),

    "ending_b": (
        "You step through the door without looking back.\n\n"
        "The evidence stays on the server. River's legacy, abandoned in "
        "a digital vault that will be wiped clean in 72 hours.\n\n"
        "The corridor is silent. You move fast, following exit signs "
        "through the empty facility. A loading dock. A steel door. "
        "And then--\n\n"
        "Rain. Cold air. Freedom.\n\n"
        "You disappear into the city, another ghost in the neon sprawl.\n\n"
        "Three weeks later, you see a news article on a coffee shop screen: "
        "\"Omnicron Industries Announces Expansion of Nexus Research Program.\" "
        "The lab is still running. The subjects are still inside.\n\n"
        "You got out. But the machine keeps turning.\n\n"
        "[dim italic]And somewhere in a room just like yours, Subject 032 "
        "wakes up confused, with nothing but a terminal...[/dim italic]"
    ),

    "ending_c": (
        "You don't send it to one person. You send it to everyone.\n\n"
        "Every journalist on River's list. Every law enforcement contact. "
        "Every regulatory body. You broadcast the evidence like a flare -- "
        "a signal fire that lights up the entire network.\n\n"
        "The building shakes. Not physically -- digitally. Every screen, "
        "every terminal, every device in Omnicron's network floods with "
        "the truth. Alarms cascade. Systems crash.\n\n"
        "You walk out of Room 31 into absolute chaos.\n\n"
        "Employees running. Security systems offline. The automated voice "
        "that once coolly announced \"all personnel\" now stutters and "
        "loops. You walk through it all like a ghost.\n\n"
        "Outside: rain, sirens, neon. The world Omnicron built is "
        "collapsing around its foundation of lies.\n\n"
        "Three days later, the company's stock is worthless. Mass arrests "
        "make the front page of every feed. Director Sable is found in "
        "a private jet grounded at Heathrow, passport revoked.\n\n"
        "And then, one week later, a message appears on a terminal you "
        "don't remember buying:\n\n"
        "[bold cyan]> You made a lot of noise. We should talk. -ZERO[/bold cyan]\n\n"
        "[bold]Maximum exposure. Maximum consequences. "
        "River would have laughed.[/bold]"
    ),
}
