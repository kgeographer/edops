# Introducing EDOPS

The **Environmental Dimensions of Place Service (EDOPS)** project assembles and delivers environmental data profiles ("signatures") for any terrestrial Earth location via an Application Programming Interface (API) <i class="bi bi-question-circle edops-help" data-help-text="TODO: define API"></i> and in the three pages of this web platform developed so far: Sandbox, Data Explorer, and Workbench. The features and functionality of these are outlined here and described in more detail in their respective sections of this documentation.

The codebase for EDOPS lives in a [Github repository](https://github.com/kgeographer/edops), and its `/documentation` folder has much additional information, including findings from the Data Characterization phase.

## What an EDOPS signature is

A signature is the environmental description of a single place, assembled on request. Around 100
variables are drawn from four global datasets:

- **BasinATLAS v1.0** — physiography, hydrology, climate, land cover, and human-footprint
  attributes, aggregated to hydrological basins. The source of most of the signature.
- **LMR v2.1** — the Last Millennium Reanalysis: annually resolved paleoclimate fields.
- **HYDE 3.4** — modelled historical land use and population, back to the early Holocene.
- **eVolv2k v4** — a reconstruction of volcanic stratospheric sulfur injection, event by event.

Values are reported for the hydrological basin containing the place you ask about, at either of two
scales. Variables are grouped into six bands that indicate how quickly each changes — and therefore
how far back a present-day measurement can reasonably be carried. See
[Premises and commitments](design/commitments.md) for why the framework is built this way, and the
[Codebook](codebook.md) for the variables themselves.

## The Sandbox page

Ask about one place and see everything EDOPS knows about it. Enter a settlement or select a
historical polity, choose how wide a scope to describe, and retrieve its signature. Seven
tabs present the result from different angles: the basin on a map, the full list of values, an
interpretive summary, the shape of the seasonal year, how typical the place is globally, and which
other basins on Earth resemble it.

Most people should start here.

## The Data Explorer page

Move from one place to the whole distribution. The Explorer maps single variables globally, compares
regions side by side, and plots any two variables against each other — for understanding how a
variable behaves across the Earth, and how variables relate to one another, before drawing
conclusions from any single place's values.

## The Workbench page

An experimental surface for putting environmental signatures alongside cultural and reference data:
ethnographic societies, ecoregions, and World Heritage cities. This is where the correspondence
questions that motivate the project are actually attempted, and it is the least settled of the
three pages.

## Why EDOPS

EDOPS is one component of **Computing Place**, a broader independent research program undertaken in
2026 by geographer [Karl Grossner, PhD.](https://kgeographer.org) EDOPS is a work in progress,
conceived as a data instrument supporting the work of a nascent sister component, **Cultural
Dimensions of Place (CDOP)**, which will investigate correspondences between cultural practices and
environmental settings.

It has become evident as the project has progressed that EDOPS could be made more broadly useful by
extending its initial cultural geography remit to historical and social science research more
generally, and to teaching.