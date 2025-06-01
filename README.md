# ZeroTier GUI

ZeroTier GUI is a simple graphical user interface for managing ZeroTier networks. It allows you to create and manage networks, add and remove members, and view network information.

The application is built using GTK 4 and Python 3, and is designed to be easy to use and understand. It is currently in development, and new features are being added regularly.

## Screenshots

![Screenshot of the networks page](screenshots/networks-page.png)

## Features

- Create and manage ZeroTier networks
- Add and remove members from networks
- View network information, including the network ID, name, and description
- View member information, including the member ID, name, and IP addresses
- Use a simple and easy-to-use graphical interface

## Getting Started

You have to get your API token from ZeroTier website and set it in the 10th line of the code in api.py (gonna change it later for .env)

To get started with ZeroTier GUI, you'll need to have ZeroTier installed and running on your system. You can then run ZeroTier GUI from the command line using the following command:

```bash
python main.py
```

## Contributing

Would be wery grateful to anyone who wants to contribute or report a bug/give a piecie of good advice how to make the app better.
Would be even more grateful if you could add some code and make the app have more sense/functionality/looks.

## F.A.Q.

- Why the hell are you trying to ask for root?
  - Do not remember the reason for this. Probably obsolete, gonna remove it.
- How do I create a network?
  - You can create a network by clicking the "Create Network" button on the "Networks" page.

## P.S

Probably will rewrite this later (with Electron) since now it's an overcomplexed messy mess, it does this and that, but i am not satisfied with it.
ZeroTier API and ZeroTier itself are dumb in my opinion.
