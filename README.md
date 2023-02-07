---

# Section Identification in Spanish Clinical Notes

Electronic Clinical Narratives (ECNs) store valuable individual's health information. 
However, there are few available open source data. Besides, ECNs can be structurally  heterogeneous, ranging from documents with  explicit section headings or titles to unstructured notes.
This lack of structure complicates building automatic systems and their evaluation.

The aim of the present work is to provide the scientific community with a Spanish open source dataset to build and evaluate automatic section identification systems. 
Together with this dataset, we make available a suitable evaluation measure.


--------------------------------------

## Sec-CodiEsp

The Sec-CodiEsp corpus is a randomly-selected subset of the background set of the CodiEsp corpus [1], consisting of 1,038 non-structured clinical records  from different medical specialties written in Spanish.
This notes are annotated with seven major sections, presenting an annotations task consisting of delimiting section boundaries and their category.


### Annotated Sections

| **Section**            | **Description**                                                                                 |
|------------------------|-------------------------------------------------------------------------------------------------|
| _Present Illness_      | Mention of the reason for consulting the specialist.                                            |
| _Derived from/to_      | Referral to the department, center or primary care physician.                                   |
| _Past Medical History_ | Mention of previous or historical pathologies.                                                  |
| _Family history_       | Mention of pathologies of family members.                                                       |
| _Exploration_          | Description of the physical examination, laboratory tests, specific studies and their results.  |
| _Treatment_            | Procedures performed on the patient to treat the patient's condition.                           |
| _Evolution_            | Evolution of the patient's health status.                                                       |


### Dataset

> **Full dataset will be made available later on.**
>> _Check the **IberLEF 2023 [ClinAIS][ClinAIS webpage]** task._

[ClinAIS webpage]: https://ixa2.si.ehu.eus/clinais/

--------------------------------------

## B2 Evaluation metric for Sec-CodiEsp Task

Existing segmentation metrics account for a variety of segmentation granularities required by this task. 
Several segmentation evaluation metrics have been proposed, WindowDiff (WD) [2], S [3] and B [4]. 

WD only measures segment boundaries and ignores segment types and therefore it was not adequate. 
S and B, both employ a variation of the editing distance with three operations (addition/deletion, substitution, and transposition), and are also well-suited to distinguish segment types. Finally we selected B as S produces excessively optimistic values due to its normalization [4]. 

* **Additions/deletions (A or D)** for full misses. _Addition_, when the prediction missed a section and adding it the gold is matched. _Deletion_ when the system predicts a non-existing section and deleting it matches the gold standard.
* **Substitutions (S)** when a boundary type is confused with another.
* **n-wise transpositions (T)** for near misses. Cases where a section type is well identified but the predicted boundary is displaced $n$ words.

The main advantage of S and B metrics is the definition of the transpose operation, in which the boundary between 2 sections can be moved by a limited and configurable number of borders, instead of performing an insert and a delete operation. Furthermore, these metrics' operations can be weighted separately allowing further adjustment based on the specific requirements for the task. 

 After an extensive analysis of the initially annotated examples, each operation's weight function was adjusted creating a new measure called B2 that can be defined using the following formulae.

* **Substitutions** undergo a high penalization as they correspond to clear errors:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?w_S(n\_substitutions)%20=%201.3%20\cdot%20n\_substitutions">
</p>

* **Additions and Deletions** generally represent discrepancies regarding whether a fragment belongs to a different section or to an existing contiguous one. This error is common given the characteristics of the documents. \
When there are exactly two additions it typically indicates the insertion of a section in the middle of another one. Under the standpoint of section identification, it should be considered as a single error, though for the algorithm it is counted as two errors: the insertion of the start of the new section and the continuation of the previous existing one. There are less frequent situations where this may not be the case, for instance if the new section spreads until the previous section's end, not being necessary the extra addition to continue the previous section. Consequently, and considering the limitations of the first version of B, it was decided to apply the next weighting:

<p align="center">
<img src="https://latex.codecogs.com/svg.image?w_A(n\_additions)%20=%20\begin{cases}%20%20%20%20%20%20%20%200%20&%20\text{if%20}%20n\_boundaries%20=%200%20\\%20%20%20%20%20%20%20%200.75%20+%20\frac{\tanh{(n\_additions%20-%201.5)%20-%202}}{4}%20&%20\text{otherwise}%20%20%20%20%20%20%20%20%20%20%20%20\end{cases}%20%20%20%20\label{eq:weight_additions}">
</p>

* **Transpositions** are minor divergences in the length of a section. Transpositions range from one or two words to complete sentences, therefore the upper limit of borders a boundary can be moved was set to $n_t=40$. This is a fairly high limit that can cover an entire paragraph, although transpositions with different displacement length do not symbolize the same error. This fact led us to weight each individual transposition based on the number of borders moved. 
The maximum value that a weighted transposition can reach is $\sim0.68$ when the boundary is moved the maximum number of borders allowed, and approaches $0$ as the displacement is smaller.

<p align="center">
<img src="https://latex.codecogs.com/svg.image?%20%20%20%20w_t(n\_borders,%20n_t)%20=%20\begin{cases}%20%20%20%20%20%20%20%200%20&%20\text{if%20}%20n\_borders%20\leq%202%20\\%20%20%20%20%20%20%20%200.35%20+%20\tanh(\frac{n\_borders-15}{10})%20/%203%20&%20\text{if%20}%202%20%3C%20n\_borders%20\leq%20n_t%20\\%20%20%20%20\end{cases}">
</p>


The next equation is used to calculate **B**, i.e., one minus the incorrectness between the 2 annotations.  
$s_1$ and $s_2$ are lists of the same size, the number of instance borders, containing in each border's position a set with a section boundary if any.

<p align="center">
<img src="https://latex.codecogs.com/svg.image?w_T(T_e,%20n_t)%20=%20\sum_{j=1}^{|T_e|}%20w_t(|\%20T_e[j][1]%20-%20T_e[j][2]\%20|,%20n_t)\\B(s_1,%20s_1,%20n_t)%20=%201%20-%20\frac{w_A(|A_e|)%20+%20w_T(T_e,%20n_t)%20+%20w_S(|S_e|)}{|A_e|%20+%20|T_e|%20+%20|S_e|%20+%20|B_M|}">
</p>

$B_M$,  $A_e$, $S_e$ and $T_e$ are calculated using $s_1$ and $s_2$, where $B_M$ is the set of matching boundary pairs, $A_e$ and $S_e$ are the sets of additions/deletions and substitutions respectively, and $T_e$ is the list of transpositions. Each transposition is a list containing among others the index of the border where the section boundary was in position 1, and in position 2 the index of the border to which the section boundary has been moved.

B metric's equation does only consider matching boundaries pairs, $B_M$, as correct section divisions, counting transpositions as an error. In the context of this task, transpositions should be taken into account towards the correctness calculation, therefore we defined the metric **B2**  based on B that considers transpositions near correct annotations. B2 uses each transposition's weight's complement to adjust how much it contributes to the correctness calculation so that small transpositions count more than bigger ones. 

<p align="center">
<img src="https://latex.codecogs.com/svg.image?%20%20%20%20B2(s_1,%20s_1,%20n_t)%20=%201%20-%20\frac{w_A(|A_e|)%20+%20w_T(T_e,%20n_t)%20+%20w_S(|S_e|)}{|A_e|%20+%20|T_e|%20+%20|S_e|%20+%20|B_M|%20+%20(|T_e|%20-%20w_T(T_e,%20n_t))}">
</p>



## References

[1] **A. Miranda-Escalada, A. Gonzalez-Agirre, M. Krallinger**, *CodiEsp corpus: gold standard Spanish clinical cases coded in ICD10 (CIE10) - eHealth CLEF2020*, 2020.
https://zenodo.org/record/3837305.

[2] **L. Pevzner, M. A. Hearst**, *A critique and improvement of an evaluation metric for text segmentation*, Computational Linguistics 28 (2002) 19–36.
https://aclanthology.org/J02-1002.

[3] **C. Fournier, D. Inkpen**, *Segmentation similarity and agreement*,  in: Human Language Technologies: Conference of the North American Chapter of the Association of Computational Linguistics, Proceedings, June 3-8, 2012, Montréal, Canada, The Association for Computational Linguistics, 2012, pp. 152–161.
https://aclanthology.org/N12-1016.

[4] **C. Fournier**, *Evaluating Text Segmentation using Boundary Edit Distance*, in: Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), Association for Computational Linguistics, Sofia, Bulgaria, 2013, pp. 1702–1712
https://aclanthology.org/P13-1167.


## Citation

> **To be announced**



## Licenses

### Dataset Content License


[`LICENSE`](LICENSE): The published Sec-CodiEsp dataset is licensed under a [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0 license button][cc-by-sa-png]][cc-by-sa]

[cc-by-sa-png]: https://i.creativecommons.org/l/by-sa/4.0/88x31.png "CC BY-SA 4.0 license button"
[cc-by-sa]: https://creativecommons.org/licenses/by-sa/4.0/ "Creative Commons Attribution-ShareAlike 4.0 International License"



### Evaluation SegEval Library License
[`evaluation/LICENSE`](evaluation/LICENSE): The evaluation library is licensed under the BSD 3-Clause license. 
The provided code is an adaptation of the [SegEval](https://github.com/cfournie/segmentation.evaluation) library which is also licensed under the BSD 3-Clause license.



---