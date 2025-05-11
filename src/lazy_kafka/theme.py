from __future__ import annotations

from textual.theme import Theme

"""$background: #000000;   /*base00*/
$primary: #5f8787;      /*base08*/
$secondary: #e78a53;    /*base0A*/
$accent: #fbcb97;
$text: #c1c1c1;         /*base05*/
$text-disabled: #333333; /*base03*/
$success: #0b6e0b;

"""
frog_theme = Theme(
    name="frog",
    primary="#5f8787",
    secondary="#fbcb97",
    accent="#e78a53",#5f8787
    foreground="#D8DEE9",
    background="#000000",
    success="#0b6e0b",#A3BE8C
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)

