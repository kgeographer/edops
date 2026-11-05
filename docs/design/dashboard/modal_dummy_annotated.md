# Environmental Profile modal: dummy contents, with unit ids

Annotated 2026-11-05 for WO-04 (wo04a). The text is `modal_dummy.md` unchanged; the ids are added. An id like `S2.1b` is section 2, sentence 1, slot b. A bracketed optional part is a unit of its own (`S1.3`) and its slots are lettered under it. Statements the Timbuktu example makes that its template does not are marked `X` and listed under the section: they show a kind of statement wanted, and are units in their own right.

Marks used below: `‹id›` follows the slot or part it labels.

---

## S1. Setting

**Template**
{Place}‹S1.1a› sits at about {elevation}‹S1.1b› m above sea level, in {terrain: flat / rolling / hilly / mountainous}‹S1.1c› country.‹S1.1› It lies in the {ecoregion}‹S1.2a› ecoregion, {one-line gist from the ecoregion summary}‹S1.2b›.‹S1.2› [The {other ecoregion}‹S1.3a› lies {distance}‹S1.3b› km to the {direction}‹S1.3c›.]‹S1.3› [Its surrounding basin also takes in parts of {ecoregion 2} and {ecoregion 3}.]‹S1.4›

**Timbuktu example: extra units**
- `S1.X1`: the gist itself says what lies "between the Sahara and the wetter savannas to the south" (a relation between ecoregions, with a direction).

## S2. Climate

**Template**
Rainfall averages about {precip}‹S2.1a› mm a year, {mostly in {months} / spread through the year}‹S2.1b›.‹S2.1› Temperatures average {temp}‹S2.2a› °C, from {coldest month mean} in {month}‹S2.2b› to {warmest month mean} in {month}‹S2.2c›.‹S2.2› [It is {among the driest / wettest / warmest / coolest} of the {N+1} basins around it.]‹S2.3›

**Timbuktu example: extra units**
- `S2.X1`: "wetter than the desert basins to the north and drier than the delta basins to the south" (a comparison with neighbours, by direction, with a class word for each neighbour).

## S3. Water

**Template**
{Place} is {distance}‹S3.1a› km from the {river name / a river}‹S3.1b› [, which drains about {upstream area} km² above this point]‹S3.1c›.‹S3.1› [Most of the water passing here falls far upstream: the catchment above is {ratio}‹S3.2a› times the size of the local basin, and {wetter / drier / cooler}‹S3.2b› than it.]‹S3.2› [A much larger river, the {name}‹S3.3a›, runs {distance}‹S3.3b› km away.]‹S3.3› [Lakes and wetlands cover about {share}% of the basin.]‹S3.4› The basin drains {to the sea about {distance} km away}‹S3.5a› / {to an inland sink about {distance} km away}‹S3.5b› / {nowhere: it is a closed basin}‹S3.5c›.‹S3.5›

**Timbuktu example: extra units**
- `S3.X1`: "Seasonal wetlands cover a large share" (a size word in place of a percentage, and "seasonal").

## S4. Land and geology

**Template**
The land is {relief description}‹S4.1a›, with {soil description: mainly sandy / clay / loamy soils}‹S4.1b›.‹S4.1› [The underlying rock is mostly {lithology class}.]‹S4.2› [{Karst / permafrost} is {extensive / present / absent}.]‹S4.3›

**Timbuktu example: extra units**
- `S4.X1`: "low and nearly level" (a relief word beyond the template's list) and "over unconsolidated sediments" (a rock statement in the soil sentence).

## S5. Land cover today

**Template**
Today about {share}% of the basin is cropland‹S5.1a› and {share}% pasture‹S5.1b›; {forest / shrubland / bare ground}‹S5.1c› covers most of the rest.‹S5.1› [Population density is about {density} per km², {higher / lower} than in most of the basins around it.]‹S5.2›

**Timbuktu example: extra units**
- `S5.X1`: "concentrated along the river" (where within the basin a cover lies).
- `S5.X2`: "sparse outside the town and the river corridor" (population by position within the basin).

## S6. Surroundings

**Template**
{Place}'s basin is one of {N+1}‹S6.1a› that meet here.‹S6.1› [Upstream, {neighbour description}‹S6.2a› drains into it; downstream, it drains into {neighbour description}‹S6.2b›.]‹S6.2› [Across the divide, the basins to the {direction}‹S6.3a› are {contrast}‹S6.3b›.]‹S6.3› [On most measures the basin resembles its neighbours.]‹S6.4› [It stands out for {variable list}.]‹S6.5›

**Timbuktu example: extra units**
- `S6.X1`: "a narrow corridor along the Niger" (the basin's shape).
- `S6.X2`: "the Niger arrives from the Inner Delta; downstream, it continues east" (a named river and a direction along it).
- `S6.X3`: "the basins to the north are desert, far drier and with almost no cropland or wetland" (a class word for neighbours, with several comparisons).

## S7. Coast and reach

**Template**
{Place} is {distance}‹S7.1a› km from the nearest coast.‹S7.1› [Its basin touches the sea.]‹S7.2› [Its nearest basin edge is the coast.]‹S7.3›

## S8. About these figures

**Template**
These figures describe the basin of about {area}‹S8.1a› km² that contains {Place}, from global datasets of about {year range}‹S8.1b›.‹S8.1› [{n} measures have no value here: {reasons}.]‹S8.2› [The point was moved {distance} m to the nearest basin.]‹S8.3›

## S9. Buttons

[Full environmental signature in EDOPS]‹S9.1› [Ecoregion on Wikipedia]‹S9.2› [Data as JSON]‹S9.3›

---

## Count of units

Sentence and bracketed-part units: S1 4, S2 3, S3 5, S4 3, S5 2, S6 5, S7 3, S8 3, S9 3 = 31. Slot units: S1 8, S2 5, S3 10, S4 2, S5 3, S6 5, S7 1, S8 2 = 36. Extra (`X`) units from the Timbuktu example: 9.

The audit step (wo04a, next) gives each unit a verdict; where every slot in a sentence has the same verdict, the sentence is one row.
