# Page 1

Gemini 2.5: Pushing the Frontier with
Advanced Reasoning, Multimodality, Long
Context, and Next Generation Agentic
Capabilities.
GeminiTeam,Google
Inthisreport,weintroducetheGemini2.Xmodelfamily: Gemini2.5ProandGemini2.5Flash,aswell
asourearlierGemini2.0FlashandFlash-Litemodels. Gemini2.5Proisourmostcapablemodelyet,
achievingSoTAperformanceonfrontiercodingandreasoningbenchmarks. Inadditiontoitsincredible
codingandreasoningskills,Gemini2.5Proisathinkingmodelthatexcelsatmultimodalunderstanding
and it is now able to process up to 3 hours of video content. Its unique combination of long context,
multimodalandreasoningcapabilitiescanbecombinedtounlocknewagenticworkflows. Gemini2.5
Flashprovidesexcellentreasoningabilitiesatafractionofthecomputeandlatencyrequirementsand
Gemini2.0FlashandFlash-Liteprovidehighperformanceatlowlatencyandcost. Takentogether,the
Gemini2.XmodelgenerationspansthefullParetofrontierofmodelcapabilityvscost,allowingusersto
exploretheboundariesofwhatispossiblewithcomplexagenticproblemsolving.
1. Introduction
Wepresentourlatestfamilyofnativelymultimodalmodelswithadvancedreasoningthroughthinking,
long context and tool-use capabilities: Gemini 2.5 Pro and 2.5 Flash and our earlier Gemini 2.0
Flash and Gemini 2.0 Flash-Lite models. Together these form a new family of highly-capable models
representing our next generation of AI models, designed to power a new era of agentic systems.
BuildinguponthefoundationoftheGemini1.5series(GeminiTeam,2024),thisGemini2.Xgeneration
brings us closer to the vision of a universal AI assistant (Hassabis, 2025).
TheGemini2.Xseriesareallbuilttobenativelymultimodal,supportinglongcontextinputsof>1
million tokens and have native tool use support. This allows them to comprehend vast datasets and
handle complex problems from different information sources, including text, audio, images, video
andevenentirecoderepositories. Theseextensivecapabilitiescanalsobecombinedtobuildcomplex
agentic systems, as happened in the case of Gemini Plays Pokémon1 (Zhang, 2025). Different models
in the series have different strengths and capabilities: (1) Gemini 2.5 Pro is our most intelligent
thinking model, exhibiting strong reasoning and code capabilities. It excels at producing interactive
web applications, is capable of codebase-level understanding and also exhibits emergent multimodal
coding abilities. (2) Gemini 2.5 Flash is our hybrid reasoning model with a controllable thinking
budget, and is useful for most complex tasks while also controlling the tradeoff between quality, cost,
and latency. (3) Gemini 2.0 Flash is our fast and cost-efficient non-thinking model for everyday tasks
and (4) Gemini 2.0 Flash-Lite is our fastest and most cost-efficient model, built for at-scale usage. A
full comparison of the models in the Gemini 2.X model family is provided in Table 1. Taken together,
the Gemini 2.X family of models cover the whole Pareto frontier of model capability vs cost, shifting
it forward across a large variety of core capabilities, applications and use-cases, see Figure 1.
The Gemini 2.5 family of models maintain robust safety metrics while improving dramatically on
1PokémonisatrademarkofNintendoCo.,Ltd.,CreaturesInc.,andGameFreakInc.
Pleasesendcorrespondencetogemini-report@google.com.
© 2025Google.Allrightsreserved
5202
luJ
22
]LC.sc[
4v16260.7052:viXra


---

# Page 2

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Gemini1.5 Gemini1.5 Gemini2.0 Gemini2.0 Gemini2.5 Gemini2.5
Flash Pro Flash-Lite Flash Flash Pro
Text,Image, Text,Image, Text,Image, Text,Image, Text,Image, Text,Image,
Inputmodalities
Video,Audio Video,Audio Video,Audio Video,Audio Video,Audio Video,Audio
Inputlength 1M 2M 1M 1M 1M 1M
Outputmodalities Text Text Text Text,Image* Text,Audio* Text,Audio*
Outputlength 8K 8K 8K 8K 64K 64K
Thinking No No No Yes* Dynamic Dynamic
Supportstooluse? No No No Yes Yes Yes
Knowledgecutoff November November June2024 June2024 January January
2023 2023 2025 2025
Table 1 | Comparison of Gemini 2.X model family with Gemini 1.5 Pro and Flash. Tool use refers
to the ability of the model to recognize and execute function calls (e.g., to perform web search,
completeamathproblem,executecode). *currentlylimitedtoExperimentalorPreview,seeSection2.7.
Information accurate as of publication date.
helpfulnessandgeneraltonecomparedtotheir2.0and1.5counterparts. Inpractice,thismeansthat
the2.5modelsaresubstantiallybetteratprovidingsaferesponseswithoutinterferingwithimportant
use cases or lecturing end users. We also evaluated Gemini 2.5 Pro’s Critical Capabilities, including
CBRN, cybersecurity, machine learning R&D, and deceptive alignment. While Gemini 2.5 Pro showed
a significant increase in some capabilities compared to previous Gemini models, it did not reach any
of the Critical Capability Levels in any area.
Our report is structured as follows: we begin by briefly describing advances we have made in
modelarchitecture,trainingandservingsincethereleaseoftheGemini1.5model. Wethenshowcase
the performance of the Gemini 2.5 models, including qualitative demonstrations of its abilities. We
conclude by discussing the safety evaluations and implications of this model series.
2. Model Architecture, Training and Dataset
2.1. Model Architecture
The Gemini 2.5 models are sparse mixture-of-experts (MoE) (Clark et al., 2022; Du et al., 2021;
Fedus et al., 2021; Jiang et al., 2024; Lepikhin et al., 2020; Riquelme et al., 2021; Roller et al., 2021;
Shazeer et al., 2017) transformers (Vaswani et al., 2017) with native multimodal support for text,
vision, and audio inputs. Sparse MoE models activate a subset of model parameters per input token
by learning to dynamically route tokens to a subset of parameters (experts); this allows them to
decouple total model capacity from computation and serving cost per token. Developments to the
model architecture contribute to the significantly improved performance of Gemini 2.5 compared to
Gemini 1.5 Pro (see Section 3). Despite their overwhelming success, large transformers and sparse
MoE models are known to suffer from training instabilities (Chowdhery et al., 2022; Dehghani et al.,
2023; Fedus et al., 2021; Lepikhin et al., 2020; Liu et al., 2020; Molybog et al., 2023; Wortsman
et al., 2023; Zhai et al., 2023; Zhang et al., 2022). The Gemini 2.5 model series makes considerable
progress in enhancing large-scale training stability, signal propagation and optimization dynamics,
resulting in a considerable boost in performance straight out of pre-training compared to previous
Gemini models.
2


---

# Page 3

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Figure 1 | Cost-performance plot. Gemini 2.5 Pro is a marked improvement over Gemini 1.5 Pro, and
has an LMArena score that is over 120 points higher than Gemini 1.5 Pro. Cost is a weighted average
of input and output tokens pricing per million tokens. Source: LMArena, imported on 2025-06-16.
Gemini 2.5 models build on the success of Gemini 1.5 in processing long-context queries, and
incorporate new modeling advances allowing Gemini 2.5 Pro to surpass the performance of Gemini
1.5Proinprocessinglongcontextinputsequencesofupto1Mtokens(seeTable3). BothGemini2.5
ProandGemini2.5Flashcanprocesspiecesoflong-formtext(suchastheentiretyof“MobyDick”or
“Don Quixote”), whole codebases, and long form audio and video data (see Appendix 8.5). Together
with advancements in long-context abilities, architectural changes to Gemini 2.5 vision processing
lead to a considerable improvement in image and video understanding capabilities, including being
able to process 3-hour-long videos and the ability to convert demonstrative videos into interactive
coding applications (see our recent blog post by Baddepudi et al., 2025).
ThesmallermodelsintheGemini2.5series—Flashsizeandbelow—usedistillation(Aniletal.,
2018; Hinton et al., 2015), as was done in the Gemini 1.5 series (Gemini Team, 2024). To reduce
the cost associated with storing the teacher’s next token prediction distribution, we approximate it
using a k-sparse distribution over the vocabulary. While this still increases training data throughput
and storage demands by a factor of k, we find this to be a worthwhile trade-off given the significant
quality improvement distillation has on our smaller models, leading to high-quality models with a
reduced serving cost (see Figure 2).
2.2. Dataset
Our pre-training dataset is a large-scale, diverse collection of data encompassing a wide range of
domainsandmodalities,whichincludespubliclyavailablewebdocuments,code(variousprogramming
languages), images, audio (including speech and other audio types) and video, with a cutoff date
of June 2024 for 2.0 and January 2025 for 2.5. Compared to the Gemini 1.5 pre-training dataset
3


---

# Page 4

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Gemini 2.5 Flash
Gemini 2.0 Flash
Gemini 2.0 Flash-Lite
o4-mini (high)
o3
Gemini 2.5 Pro Company
Grok 3 Google
OpenAI
Claude 4 Opus (Extended Thinking)
Anthropic
Claude 4 Sonnet (Extended Thinking) DeepSeek
xAI
DeepSeek R1 0528 (May '25)
0 50 100 150 200 250 300 350
Output Tokens per Second
Figure 2 | Number of output tokens generated per second (after the first chunk has been received
from the API) for different models. Source: ArtificialAnalysis.ai, imported on 2025-06-15.
we also utilized new methods for improved data quality for both filtering, and deduplication. Our
post-training dataset, like Gemini 1.5, consists of instruction tuning data that is carefully collected
andvetted. Itisacollectionofmultimodaldatawithpairedinstructionsandresponses,inadditionto
human preference and tool-use data.
2.3. Training Infrastructure
This model family is the first to be trained on TPUv5p architecture. We employed synchronous
data-parallel training to parallelise over multiple 8960-chip pods of Google’s TPUv5p accelerators,
distributed across multiple datacenters.
Themainadvancesinsoftwarepre-traininginfrastructurecomparedwithGemini1.5wererelated
to elasticity and mitigation of SDC (Silent Data Corruption) errors:
1. Slice-Granularity Elasticity: Our system now automatically continues training with fewer
“slices” of TPU chips when there is a localized failure, and this reconfiguration results in tens
of seconds of lost training time per interruption, compared with the 10 or more minute delay
waitingforhealthymachinestoberescheduledwithoutelasticity;thesystemcontinuestraining
at around 97% throughput while the failed slice is recovering. At the scale of this training run
we see interruptions from hardware failures multiple times per hour, but our fault tolerance
machinery is designed to tolerate the higher failure rates expected at much larger scales.
2. Split-Phase SDC Detection: On previous large-scale runs it could take many hours to detect
and localize machines with SDC errors, requiring both downtime while debugging, and roll-
back/replay of a large number of potentially corrupt training steps. We now use lightweight
deterministic replay to immediately repeat any step with suspicious metrics, and compare
per-deviceintermediatechecksumstolocalizetherootcauseofanydatacorruption. Empirically,
accelerators that start to exhibit intermittent SDCs are identified within a few minutes, and
quickly excluded from the job. During this run, around 0.25% of steps were replayed due to
suspected SDCs and 6% of these replays turned out to be genuine hardware corruption.
Both of the above techniques were relatively simple to implement due to the single-controller
design of the Pathways system (Barham et al., 2022), which allows all accelerators to be coordinated
from a single python program with a global view of the system state. The controller can make use of
4

|  |  |  |  |  |  |  |  |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  | Co |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |


---

# Page 5

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
AIME GPQA (Diamond) LiveCodeBench v5
100
2.0 Flash (No Thinking)
2.0 Flash (Thinking)
2.5 Flash (Dynamic Thinking)
80 2.5 Pro (Dynamic Thinking)
60
40
20
0
Figure 3 | Impact of “Thinking” on Gemini’s performance on AIME 2025 (Balunović et al., 2025),
LiveCodeBench (corresponding to 10/05/2024 - 01/04/2025 in the UI) (Jain et al., 2024) and GPQA
diamond (Rein et al., 2024) benchmarks.
parallel ‘remote python’ operations on TPU workers to monitor training metrics, track performance
stragglers, and root-cause SDC errors.
Overall during the run, 93.4% of the time was spent performing TPU computations; the re-
mainder was approximately spent half in elastic reconfigurations, and half in rare tail cases where
elasticity failed. Around 4.5% of the computed steps were replays or rollbacks for model debugging
interventions.
2.4. Post-training
Since the initial announcement of Gemini 1.5, significant advancements have been made in our
post-training methodologies, driven by a consistent focus on data quality across the Supervised
Fine-Tuning (SFT), Reward Modeling (RM), and Reinforcement Learning (RL) stages. A key focus
has been leveraging the model itself to assist in these processes, enabling more efficient and nuanced
quality control.
Furthermore,wehaveincreasedthetrainingcomputeallocatedtoRL,allowingdeeperexploration
and refinement of model behaviors. This has been coupled with a focus on verifiable rewards
and model-based generative rewards to provide more sophisticated and scalable feedback signals.
Algorithmic changes to the RL process have also improved stability during longer training. These
advancements have enabled Gemini 2.5 to learn from more diverse and complex RL environments,
including those requiring multi-step actions and tool use. The combination of these improvements in
dataquality,increasedcompute,algorithmicenhancements,andexpandedcapabilitieshascontributed
toacross-the-boardperformancegains(asdescribedinSection3),notablyreflectedinthesignificant
increase in the model’s LMArena Elo scores, with both Gemini 2.5 Flash and Pro gaining more than
110 points over their Gemini 1.5 counterparts (122 for Gemini 2.5 Pro and 111 for Gemini 2.5 Flash,
see Figure 1), along with significant improvements on several other frontier benchmarks.
2.5. Thinking
Past Gemini models produce an answer immediately following a user query. This constrains the
amount of inference-time compute (Thinking) that our models can spend reasoning over a problem.
Gemini Thinking models are trained with Reinforcement Learning to use additional compute at
inference time to arrive at more accurate answers. The resulting models are able to spend tens of
5
)%(
etar
ssaP
/
ycaruccA


---

# Page 6

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
AIME 2025 LiveCodeBench GPQA diamond
90 80 88
75
85 86
70
80 65 84
75 60 82
55
70 80
50
65 45 78
1024 2048 4096 8192 16384 32768 1024 2048 4096 8192 16384 32768 1024 2048 4096 8192 16384 32768
Thinking Budget (number of tokens) Thinking budget (number of tokens) Thinking budget (number of tokens)
Figure 4 | Impact of thinking budget on performance on AIME 2025 (Balunović et al., 2025), Live-
CodeBench (corresponding to 10/05/2024 - 01/04/2025 in the UI) (Jain et al., 2024) and GPQA
diamond (Rein et al., 2024) benchmarks.
thousands of forward passes during a “thinking” stage, before responding to a question or query.
Our training recipe has evolved from the original experimental thinking model, Gemini 2.0 Flash
Thinking (launched in December 2024), to the Gemini 2.5 Thinking series, which incorporates
Thinkingnativelyacrossalldomains. Theresultisasinglemodelthatcanachievestrongerreasoning
performanceacrosstheboard,andisabletoscaleupitsperformancefurtherasafunctionofinference
time (see Figure 3 for an example of the impact of Thinking).
WeintegratedThinkingwithotherGeminicapabilities,includingnativemultimodalinputs(images,
text, video, audio) and long context (1M+ tokens). For any of these capabilities, the model decides
for itself how long to think before providing an answer. We also provide the ability to set a Thinking
budget, constraining the model to respond within a desired number of tokens. This allows users to
trade off performance with cost. To demonstrate this capability, we conducted experiments where we
systematically varied the thinking budget, measured in the number of tokens the model is allowed to
use for internal computation. As shown in Figure 4, increasing this budget allows the model to scale
its performance and achieve significantly higher accuracy.
2.6. Capability-specific improvements
WhilemostofthechangesmadetoourtrainingarchitectureandrecipesinceGemini1.5haveresulted
in improvements across all capabilities, we have also made changes that have resulted in some
capability-specific wins. We will now discuss these for code, factuality, long context, multilinguality,
audio, video, and agentic use cases (with a particular focus on Gemini Deep Research).
Code
Gemini 2.0 and 2.5 represent a strategic shift of our development priorities towards delivering
tangiblereal-worldvalue,empoweringuserstoaddresspracticalchallengesandachievedevelopment
objectives within today’s complex, multimodal software environments. To realize this, concerted
efforts have been undertaken across both pre-training and post-training phases since Gemini 1.5.
In pre-training, we intensified our focus on incorporating a greater volume and diversity of code
data from both repository and web sources into the training mixture. This has rapidly expanded
coverage and enabled the development of more compute-efficient models. Furthermore, we have
substantially enhanced our suite of evaluation metrics for assessing code capabilities aligned with
downstream use cases, alongside improving our ability to accurately predict model performance.
6
)%(
etar
ssaP
/ ycaruccA


---

# Page 7

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Duringpost-training,wedevelopednoveltrainingtechniquesincorporatingreasoningcapabilitiesand
curatedadiversesetofengineeringtasks,withtheaimtoequipGeminiwitheffectiveproblem-solving
skills crucial for addressing modern engineering challenges. Key applications demonstrating these
advancements include IDE functionalities, code agent use cases for complex, multi-step operations
within full repositories, and multimodal, interactive scenarios such as end-to-end web and mobile
application development. Collectively, these efforts have yielded broad and significant improvements
in Gemini’s coding capabilities. This progress is evidenced by superior performance on established
benchmarks: performance on LiveCodeBench (Jain et al., 2024) increased from 30.5% for Gemini
1.5 Pro to 74.2% for Gemini 2.5 Pro, while that for Aider Polyglot (Gauthier, 2025) went from
16.9% to 82.2%. Performance on SWEBench-verified (Chowdhury et al., 2024; Jimenez et al., 2024)
went from 34.2% to 67.2%, see Table 3 and Figure 5 in Section 3.2. Furthermore, Gemini 2.5 Pro
obtained an increase of over 500 Elo over Gemini 1.5 Pro on the LMArena WebDev Arena (Chiang
et al., 2024; LMArena Team, 2025), resulting in meaningful enhancements in practical applications,
including UI and web application development (Doshi, 2025a), and the creation of sophisticated
agentic workflows (Kilpatrick, 2025).
Factuality
Within the context of generative models, ensuring the factuality of model responses to information-
seeking prompts remains a core pillar of Gemini model development. With Gemini 1.5, our research
was concentrated on enhancing the model’s world knowledge and its ability to provide answers
faithfullygroundedinthecontextprovidedwithintheprompt. ThiseffortculminatedintheDecember
2024 release of FACTS Grounding (Jacovi et al., 2025), now an industry-standard benchmark for
evaluating an LLM’s capacity to generate responses grounded in user-provided documents. With
Gemini 2.0 and 2.5, we have significantly expanded our scope to address multimodal inputs, long-
context reasoning, and model-retrieved information. At the same time, the landscape and user
expectations for factuality have evolved dramatically, shaped in part by Google’s deployment of AI
Overviews and AI Mode (Stein, 2025). To meet these demands, Gemini 2.0 marked a significant leap
as our first model family trained to natively call tools like Google Search, enabling it to formulate
precisequeriesandsynthesizefreshinformationwithsources. Buildingonthis,Gemini2.5integrates
advancedreasoning,allowingittointerleavethesesearchcapabilitieswithinternalthoughtprocesses
to answer complex, multi-hop queries and execute long-horizon tasks. The model has learned to use
search and other tools, reason about the outputs, and issue additional, detailed follow-up queries
to expand the information available to it and to verify the factual accuracy of the response. Our
latest models now power the experiences of over 1.5B monthly active users in Google’s AI Overviews
and 400M users in the Gemini App. These models exhibit state-of-the-art performance across a
suite of factuality benchmarks, including SimpleQA for parametric knowledge (Wei et al., 2024),
FACTSGroundingforfaithfulnesstoprovideddocuments(Jacovietal.,2024,2025),andtheVectara
Hallucination Leaderboard (Hughes et al., 2023), cementing Gemini as the model of choice for
information-seeking demands.
Long context
Modeling and data advances helped us improve the quality of our models’ responses to queries
utilizingouronemillion-lengthcontextwindow,andwereworkedourinternalevaluationstobemore
challengingtohelpsteerourmodelingresearch. Whenhill-climbing,wetargetedchallengingretrieval
tasks (like LOFT of Lee et al., 2024), long-context reasoning tasks (like MRCR-V2 of Vodrahalli et al.,
2024), and multimodal tasks (like VideoMME of Fu et al., 2025). According to the results in Table 6,
the new 2.5 models improve greatly over previous Gemini 1.5 models and achieve state-of-the-art
quality on all of those. An example showcasing these improved capabilities for video recall can be
7


---

# Page 8

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
seen in Appendix 8.5, where Gemini 2.5 Pro is able to consistently recall a 1 second visual event out
of a full 46-minute video.2
Multilinguality
Gemini’s multilingual capabilities have also undergone a profound evolution since 1.5, which already
encompassed over 400 languages via pretraining. This transformation stems from a holistic strategy,
meticulously refining pre- and post-training data quality, advancing tokenization techniques, innovat-
ing core modeling, and executing targeted capability hillclimbing. The impact is particularly striking
in Indic and Chinese, Japanese and Korean languages, where dedicated optimizations in data quality
andevaluationhaveunlockeddramaticgainsinbothqualityanddecodingspeed. Consequently,users
benefit from significantly enhanced language adherence, responses designed to faithfully respect the
requested output language, and a robust improvement in generative quality and factuality across
languages, solidifying Gemini’s reliability across diverse linguistic contexts.
Audio
While Gemini 1.5 was focused on native audio understanding tasks such as transcription, translation,
summarization and question-answering, in addition to understanding, Gemini 2.5 was trained to
perform audio generation tasks such as text-to-speech or native audio-visual to audio out dialog. To
enable low-latency streaming dialog, we incorporated causal audio representations that also allow
streaming audio into and out of Gemini 2.5. These capabilities derive from an increased amount of
pre-training data spanning over 200 languages, and development of improved post-training recipes.
Finally, through our improved post-training recipes, we have integrated advanced capabilities such as
thinking, affective dialog, contextual awareness and tool use into Gemini’s native audio models.
Video
We have significantly expanded both our pretraining and post-training video understanding data,
improving the audio-visual and temporal understanding capabilities of the model. We have also
trainedourmodelssothattheyperformcompetitivelywith66insteadof258visualtokensperframe,
enabling using about 3 hours of video instead of 1h within a 1M tokens context window3. Two
new applications that were not previously possible, but that have been unlocked as a result of these
changes are: creating an interactive app from a video (such as a quiz to test students’ understanding
of the video content) and creating a p5.js animation to show the key concepts from the video. Our
recent blog post (Baddepudi et al., 2025) shows examples of these applications.
Gemini as an Agent: Deep Research
Gemini Deep Research (Gemini Team, Google, 2024) is an agent built on top of the Gemini 2.5 Pro
modeldesignedtostrategicallybrowsethewebandprovideinformedanswerstoeventhemostniche
user queries. The agent is optimized to perform task prioritization, and is also able to identify when
it reaches a dead-end when browsing. We have massively improved the capabilities of Gemini Deep
Research since its initial launch in December 2024. As evidence of that, performance of Gemini
Deep Research on the Humanity’s Last Exam benchmark (Phan et al., 2025) has gone from 7.95% in
December 2024 to the SoTA score of 26.9% and 32.4% with higher compute (June 2025).
2Forfurtherdiscussiononlongcontextcapabilities,challenges,andfutureoutlook,theReleaseNotespodcastepisode
“DeepDiveintoLongContext”providesadditionalinsightsanddiscussion:https://youtu.be/NHMJ9mqKeMQ.
3ThisisreferredtoaslowmediaresolutionintheAPI:https://ai.google.dev/api/generate-content#Media
Resolution.
8


---

# Page 9

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
2.7. The path to Gemini 2.5
On the way to Gemini 2.5 Pro, we experimented with our training recipe, and tested a small number
of these experimental models with users. We have already discussed Gemini 2.0 Flash Thinking (see
Section 2.5). We will now discuss some of the other models briefly.
Gemini 2.0 Pro
In February 2025, we released an experimental version of Gemini 2.0 Pro. At the time, it had
the strongest coding performance of any model in the Gemini model family, as well as the best
understanding and world knowledge. It also came with our largest context window at 2 million
tokens, which enabled it to comprehensively analyze and understand vast amounts of information.
For further information about Gemini 2.0 Pro, please see our earlier blog posts (Kavukcuoglu, 2025;
Mallick and Kilpatrick, 2025).
Gemini 2.0 Flash Native Image Generation Model
In March 2025, we released an experimental version of Gemini 2.0 Flash Native Image Generation.
It has brought to the users new capabilities as a result of a strong integration between the Gemini
model and image-generation capabilities, enabling new experiences related to image generation &
image editing via natural-language prompting. Capabilities such as multi-step conversational editing
orinterleavedtext-imagegenerationareverynaturalinsuchasetting,andhorizontaltransferrelated
tomulti-languagecoverageimmediatelyallowedsuchexperiencestohappenacrossallthelanguages
supported by the Gemini models. Native image generation turns Gemini into a multimodal creation
partner and enables Gemini to express ideas through both text and images, and to seamlessly move
between the two. For further information about Gemini 2.0 Flash Native Image Generation, please
see our earlier blog posts (Kampf and Brichtova, 2025; Sharon, 2025)
Gemini 2.5 Audio Generation
With Gemini 2.5, the Controllable TTS and Native Audio Dialog capabilities are available as separate
options on AI Studio (Generate Media and Stream sections respectively). Our Gemini 2.5 Preview
TTS Pro and Flash models support more than 80 languages with the speech style controlled by a free
formatted prompt which can specify style, emotion, pace, etc, while also being capable of following
finer-grained steering instructions specified in the transcript. Notably, Gemini 2.5 Preview TTS can
generatespeechwithmultiplespeakers,whichenablesthecreationofpodcastsasusedinNotebookLM
AudioOverviews(Wang,2024). OurGemini2.5FlashPreviewNativeAudioDialogmodelusesnative
audio generation, which enables the same level of style, pacing and accent control as available in our
controllable TTS offering. Our dialog model supports tool use and function calling, and is available
in more than 24 languages. With native audio understanding and generation capabilities, it can
understandandrespondappropriatelytotheuser’stone. Thismodelisalsocapableofunderstanding
when to respond to the user, and when not to respond, ignoring background and non-device directed
audio. Finally, we also offer an advanced ‘Thinking’ variant that effectively handles more complex
queries and provides more robust and reasoned responses in exchange for some additional latency.
Gemini 2.5 Flash-Lite
In June 2025, we released an experimental version of Gemini 2.5 Flash-Lite (gemini-2.5-flash-
lite-preview-06-17). ItcomeswiththesamecapabilitiesthatmakeGemini2.5helpful,including
the ability to turn thinking on at different budgets, connecting to tools like Google Search and code
9


---

# Page 10

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
execution,supportformultimodalinputsanda1million-tokencontextlength. Ourgoalwastoprovide
an economical model class which provides ultra-low-latency capabilities and high throughput per
dollar, echoing the initial release of 2.0 Flash-Lite (Google DeepMind, 2025b; Mallick and Kilpatrick,
2025).
Gemini 2.5 Pro Deep Think
To advance Gemini’s capabilities towards solving hard reasoning problems, we developed a novel
reasoning approach, called Deep Think, that naturally blends in parallel thinking techniques during
response generation. Deep Think enables Gemini to creatively produce multiple hypotheses and
carefully critique them before arriving at the final answer, achieving state-of-the-art performances in
challengingbenchmarkssuchasOlympiadmath(USAMO2025),competitivecoding(LiveCodeBench),
and multimodality (MMMU), see more details at (Doshi, 2025b). We announced Gemini 2.5 Deep
Think at Google I/O and launched an experimental version to trusted testers and advanced users in
June 2025.
10


---

# Page 11

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
3. Quantitative evaluation
LiveCodeBench Aider Polyglot SWE-bench Verified
100 100 100
Gemini version
1.5
80 2.0 80 80
2.5
60 60 60
40 40 40
20 20 20
0 0 0
Flash Pro Flash Pro Flash Pro
GPQA (diamond) AIME 2025 HiddenMath-Hard
100 100 100
80 80 80
60 60 60
40 40 40
20 20 20
0 0 0
Flash Pro Flash Pro Flash Pro
Figure 5 | Performance of Gemini 2.X models at coding, math and reasoning tasks in comparison to
previous Gemini models. SWE-bench verified numbers correspond to the “multiple attempts” setting
reported in Table 3.
We will now examine the performance of the Gemini 2.X model family across a wide range of
benchmarks. We will first compare the performance of the Gemini 2.X models to the earlier Gemini
1.5 Pro and Flash models, before we compare the performance of Gemini 2.5 Pro to other available
large language models.
With web-scale pre-training of AI models, coupled with the post-training techniques that allow
policy and reward models to leverage public benchmarks, avoiding leaks and biases in the data used
for pre- and post-training is a persistent challenge. In the development of the Gemini 2.5 series, in
addition to the standard n-gram based decontamination we used in Gemini 1.5, we also employed
semantic-similarity and model based decontamination procedures to help mitigate evaluation set
leakage. Tomovebeyondtherelianceontrainingsetdecontamination,wealsocontinuereportingon
internally developed non-public benchmarks, such as HiddenMath.
Model AIStudiomodelID
Gemini1.5Flash gemini-1.5-flash-002
Gemini1.5Pro gemini-1.5-pro-002
Gemini2.0Flash-Lite gemini-2.0-flash-lite-001
Gemini2.0Flash gemini-2.0-flash-001
Gemini2.5Flash gemini-2.5-flash
Gemini2.5Pro gemini-2.5-pro
Table 2 | Mapping of Gemini model names to AI Studio API model IDs.
11
)%(
etar
ssaP
)%(
ycaruccA

| Gemini version
1.5
2.0
2.5 |  |  |
|---|---|---|
|  |  |  |
|  |  |  |

|  |
|---|
|  |

|  |  |
|---|---|
|  |  |

|  |  |
|---|---|
|  |  |

|  |  |
|---|---|
|  |  |

|  |  |
|---|---|
|  |  |

|  |  |  |
|---|---|---|
|  |  |  |
|  |  |  |

|  |  |  |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

|  |  |
|---|---|
|  |  |

|  |  |
|---|---|
|  |  |

|  |  |
|---|---|
|  |  |

|  |  |  |
|---|---|---|
|  |  |  |
|  |  |  |

|  |  |
|---|---|
|  |  |


---

# Page 12

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
3.1. Methodology
In Table 3, we compare the performance of Gemini 2.5 models to the Gemini 1.5 models, while in
Table 4, we compare the performance of Gemini 2.5 Pro to that of other large language models.
Gemini results: AllGeminiscoresarepass@1,andare“singleattempt”settingsunlessotherwise
specified. Inthe“singleattempt”setting,nomajorityvotingorparalleltest-timecomputeispermitted,
while in the “multiple attempts” setting, test-time selection of the candidate answer is allowed. All
Gemini evaluations are run with the AI Studio API for the model id that we provide in Table 2, with
defaultsamplingsettings. Toreducevariance,weaverageovermultipletrialsforsmallerbenchmarks.
AiderPolyglotscoresarethepassrateaverageof3trials. Vibe-EvalresultsarereportedusingGemini
as a judge.
Non-Gemini results: All the results for non-Gemini models are sourced from providers’ self
reported numbers unless mentioned otherwise. All “SWE-bench Verified” numbers follow official
providerreports,whichmeansthattheyarecomputedusingdifferentscaffoldingsandinfrastructure,
and aren’t directly comparable.
For some evaluations, we obtain results from the external leaderboards that report results on
these benchmarks. Results for Humanity’s Last Exam results are sourced from Scale’s leaderboard
andresultsforDeepSeekareobtainedfromthetext-onlyvariantoftheleaderboard(indicatedwitha
⋄in Table 4). For Gemini 2.0 models, the reported results are on an earlier HLE dataset (indicated
with a † in Table 3). Results on LiveCodeBench results are taken from (1/1/2025 - 5/1/2025) in the
UI. Aider Polyglot numbers come from the Aider leaderboard and results for SimpleQA come from
this repo where available. Results on FACTS Grounding come from Kaggle. In the case of LOFT and
MRCR-V2,wereportresultsonboththe128kcontextlengthvariant,aswellasthe1Mcontextlength
variant. In the 128k context length variant, we measure performance on contexts up to 128k, while
for the 1M context length variant, we report performance on context lengths of exactly 1M.
More details on all benchmarks, including subsets and how scores were obtained can be found in
Table 11 in Appendix 8.1.
3.2. Core capability quantitative results
As can be seen in Table 3, and Figure 5, the Gemini 2.5 models excel at coding tasks such as
LiveCodeBench, Aider Polyglot and SWE-bench Verified, and represent a marked improvement over
previous models.
Inadditiontocodingperformance,Gemini2.5modelsarenoticeablybetteratmathandreasoning
tasks than Gemini 1.5 models: performance on AIME 2025 is 88.0% for Gemini 2.5 Pro compared to
17.5% for Gemini 1.5 Pro, while performance on GPQA (diamond) went from 58.1% for Gemini 1.5
Pro to 86.4%. Performance on image understanding tasks has also increased significantly.
It is also interesting to note that the Gemini 2.5 Flash model has become the second most capable
model in the Gemini family, and has overtaken not just previous Flash models, but also the Gemini
1.5 Pro model released one year ago.
12


---

# Page 13

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Gemini1.5 Gemini1.5 Gemini2.0 Gemini2.0 Gemini2.5 Gemini2.5
Capability Benchmark
Flash Pro Flash-Lite Flash Flash Pro
LiveCodeBench 30.3% 29.7% 29.1% 29.1% 59.3% 74.2%
AiderPolyglot 2.8% 16.9% 10.5% 21.3% 56.7% 82.2%
single
9.6% 22.3% 12.5% 21.4% 48.9% 59.6%
Code SWE-bench attempt
multiple
Verified 19.7% 34.2% 23.1% 34.2% 60.3% 67.2%
attempts
GPQA
50.0% 58.1% 50.5% 65.2% 82.8% 86.4%
(diamond)
Reasoning
Humanity’s
notools - 4.6% 4.6%† 5.1%† 11.0% 21.6%
LastExam
SimpleQA 8.6% 24.9% 16.5% 29.9% 26.9% 54.0%
Factuality FACTS
82.9% 80.0% 82.4% 84.6% 85.3% 87.8%
Grounding
GlobalMMLU
72.5% 80.8% 78.0% 83.4% 88.4% 89.2%
Multilinguality (Lite)
ECLeKTic 16.4% 27.0% 27.7% 33.6% 36.8% 46.8%
AIME2025 14.7% 17.5% 23.8% 29.7% 72.0% 88.0%
Math
HiddenMath- 36.8% 44.3% 47.4% 53.7% 75.5% 80.5%
Hard
LOFT(hard ≤128K 67.3% 75.9% 50.7% 58.0% 82.1% 87.0%
retrieval) 1M 36.7% 47.1% 7.6% 7.6% 58.9% 69.8%
Long-context
MRCR-V2 ≤128K 18.4% 26.2% 11.6% 19.0% 54.3% 58.0%
(8-needle) 1M 10.2% 12.1% 4.0% 5.3% 21.0% 16.4%
MMMU 58.3% 67.7% 65.1% 69.3% 79.7% 82.0%
Vibe-Eval
52.3% 55.9% 51.5% 55.4% 65.4% 67.2%
Image (Reka)
Understanding
ZeroBench 0.5% 1.0% 0.75% 1.25% 2.0% 4.5%
BetterChartQA 59.0% 65.8% 52.3% 57.8% 67.3% 72.4%
Table 3 | Evaluation of Gemini 2.5 family across a wide range of core capability benchmarks and in
comparison to Gemini 1.5 models. Please see Tables 5 and 6 for audio and video evaluations. See
Table 11 Appendix 8.1 for benchmarks and evaluation details.
13


---

# Page 14

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
3.3. Evaluation of Gemini 2.5 Pro against other large language models
Relative to other large language models that are available (see Table 4), Gemini achieves the highest
scoreontheAiderPolyglotcodingtask,Humanity’sLastExam,GPQA(diamond),andontheSimpleQA
and FACTS Grounding factuality benchmarks out of all of the models examined here. Gemini also
continues to stand out for achieving the SoTA score on both the LOFT and MRCR long-context tasks
at 128k context, and is the only one, amongst the models examined in the above table, to support
context lengths of 1M+ tokens.
Not all of the models shown in Table 4 have native support for multimodal inputs. As such, we
compare against a different set of models for audio and video understanding.
Audio Understanding
In Table 5, we showcase the performance of the Gemini 2.5 model family at audio understanding,
and compare the performance of these models to earlier Gemini models, as well as to GPT models.
Gemini2.5Prodemonstratesstate-of-the-artaudiounderstandingperformanceasmeasuredbypublic
benchmarks for ASR and AST, and compares favorably to alternatives under comparable testing
conditions (using the same prompts and inputs).
Video Understanding
In Table 6, we show the performance of Gemini 2.5 models at video understanding. As can be
seen, Gemini 2.5 Pro achieves state-of-the-art performance on key video understanding benchmarks,
surpassing recent models like GPT 4.1 under comparable testing conditions (same prompt and video
Gemini2.5 o3 o4-mini Claude4 Claude4 Grok3Beta DeepSeekR1
Capability Benchmark
Pro high high Sonnet Opus ExtendedThinking 0528
LiveCodeBench 74.2% 72.0% 75.8% 48.9% 51.1% – 70.5%
Code
AiderPolyglot 82.2% 79.6% 72.0% 61.3% 72.0% 53.3% 71.6%
single 59.6% 69.1% 68.1% 72.7% 72.5% - -
SWE-bench attempt
Verified multiple 67.2% - - 80.2% 79.4% - 57.6%
attempts
GPQA
single 86.4% 83.3% 81.4% 75.4% 79.6% 80.2% 81.0%
Reasoning (diamond) attempt
Humanity’s
no 21.6% 20.3% 18.1% 7.8% 10.7% - 14.0%⋄
LastExam tools
SimpleQA 54.0% 48.6% 19.3% - - 43.6% 27.8%
Factuality
FACTS
87.8% 69.9% 62.1% 79.1% 77.7% 74.8% 82.4%
Grounding
Math AIME2025 single 88.0% 88.9% 92.7% 70.5% 75.5% 77.3% 87.5%
attempt
LOFT(hard ≤128K 87.0% 77.0% 60.5% 81.6% - 73.1% -
retrieval) 1M 69.8% - - - - - -
Long-context
MRCR-V2 ≤128K 58.0% 57.1% 36.3% 39.1% 16.1%* 34.0% -
(8-needle) 1M 16.4% - - - - - -
Image
MMMU single 82.0% 82.9% 81.6% 74.4% 76.5% 76.0% NoMMsupport
Understanding attempt
Table 4 | Performance comparison of Gemini 2.5 Pro with other large language models on different
capabilities. Please see Tables 5 and 6 for audio and video evaluations. See Table 11 for benchmarks
and evaluation details. *: with no thinking and API refusals
14


---

# Page 15

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
Gemini1.5 Gemini1.5 Gemini2.0 Gemini2.0 Gemini2.5 Gemini2.5 GPT-4omini GPT4o GPT4o
Benchmark
Flash Pro Flash-Lite Flash Flash Pro AudioPreview AudioPreview transcribe
FLEURS
12.71 7.14 9.60 9.04 9.95 6.66 19.52 12.16 8.17
(53lang,WER↓)
CoVoST2
34.81 37.53 34.74 36.35 36.15 38.48 29.5 35.89 –
(21lang,BLEU↑)
Table 5 | Performance comparison of Gemini 2.5 models to earlier Gemini models, as well as to GPT
models for audio understanding. Note that for GPT models, metrics may differ from those previously
reported due to differing eval methodologies. See Table 11 for benchmarks and evaluation details.
frames). For cost-sensitive applications, Gemini 2.5 Flash provides a highly competitive alternative.
Gemini1.5 Gemini1.5 Gemini2.0 Gemini2.0 Gemini2.5 Gemini2.5 OpenAI
Modalities Benchmark
Flash Pro Flash-Lite Flash Flash Pro GPT4.1
ActivityNet-QA 56.2 57.3 55.3 56.4 65.1 66.7 60.4
EgoTempo 34.5 36.3 30.1 39.3 36.7 44.3 40.3
PerceptionTest 66.5 69.4 67.5 68.8 75.1 78.4 64.8
visual-only
QVHighlights 64.4 68.7 25.7 63.9 52.4 75.0 71.4
VideoMMMU 64.8 70.4 64.3 68.5 79.2 83.6 60.9
1H-VideoQA 61.9 72.2 55.6 67.5 67.5 81.0 56.8
LVBench 61.9 65.7 52 61.8 62.7 78.7 63.4
VideoMME 70.4 73.2 62.1 72.8 75.5 84.3 72.0
audio+visual VATEX 56.9 55.5 58.5 56.9 65.2 71.3 64.1
VATEX-ZH 46.2 52.2 43.2 48.5 43.9 59.7 48.7
YouCook2Cap 153.2 170.0 78.6 129.0 177.6 188.3 127.6
Minerva 49.6 52.8 46.8 52.4 60.7 67.6 54.0
visual+subtitles
Neptune 78.7 82.7 81.5 83.1 84.3 87.3 85.2
audio+visual+
VideoMME 77.3 79.8 72.5 78.8 81.5 86.9 79.6
subtitles
Table 6 | Evaluation of Gemini 2.5 vs. prior models and GPT 4.1 on video understanding benchmarks.
Performance is measured by string-match accuracy for multiple-choice VideoQA, LLM-based accuracy
for open-ended VideoQA, R1@0.5 for moment retrieval and CIDEr for captioning. See Table 11 for
benchmarks and evaluation details.
15


---

# Page 16

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
4. Example use cases of Gemini 2.5 Pro
4.1. Gemini Plays Pokémon
Gemini 2.5 Pro Plays Pokemon Progress Timeline
Hall of Fame
Beat Elite Four Lance
Beat Elite Four Agatha
Beat Elite Four Bruno
Beat Elite Four Lorelei
Exit Victory Road (1st)
Enter Victory Road (1st)
Rival 7 (Route 22 #2)
Earth Badge
Volcano Badge
Acquire Secret Key (Pokemon Mansion)
Enter Cinnabar Island (1st)
Marsh Badge
Rocket Boss 2 (Silph Co.)
Rival 6 (Silph Co.)
Enter Silph Co. (1st)
Enter Saffron City (1st)
Acquire HM04 Strength (Warden's Teeth)
Soul Badge
Acquire HM03 Surf (Beat Safari Zone)
Enter Safari Zone (1st)
Enter Fuchsia City (1st)
Acquire PokéFlute (Rescue Fuji)
Rainbow Badge
Rocket Boss 1 (Rocket Hideout)
Enter Rocket Hideout (1st)
Enter Celadon City (1st)
Rival 5 (Lavender Tower)
Exit Rock Tunnel & Reach Lavender Town (1st)
Access Pokemon w/ Flash
Enter Rock Tunnel (1st)
Thunder Badge
Acquire HM05 Flash
Access Pokemon w/ CUT
Rival 4 (SS Anne)
Bill’s House
Cascade Badge
Rival 3 (Nugget Bridge)
Exit Mt. Moon (1st)
Enter Mt. Moon (1st)
Boulder Badge
Exit Viridian Forest (1st)
Enter Viridian Forest (1st) Run 1
Viridian City Run 2 (Actual)
Rival 1 (Oak's Lab)
0 100 200 300 400 500 600 700 800
Time Elapsed (Hours)
Figure 6 | Progression of the Gemini Plays Pokémon agent through the game, across two runs. Run 1
wasthedevelopmentrunwherechangestotheharnesswereperformed. Run2isthefullyautonomous
runwiththefinalfixedscaffold. Bothrunshavethesamestarter(Squirtle). Theeventsareorderedon
the y-axis by the order they happened, following the order of Run 2 when there is a conflict. Notably,
theGPPagentadditionallywentthroughthedifficult(andoptional)SeafoamIslandsdungeoninRun
2, while in Run 1, GPP reached Cinnabar Island via Pallet Town and Route 21.
On March 28, 2025, an independent developer not affiliated with Google, Joel Zhang, set up a
Twitch stream (Gemini Plays Pokémon, or GPP) for Gemini 2.5 Pro (Gemini 2.5 Pro Exp 03-25) to
play Pokémon Blue on stream (Zhang, 2025) as an experiment to better understand how well the
model was capable of playing Pokémon (in a similar spirit to Claude Plays Pokémon, see Anthropic
2025). In this initial run through the game, the goal was to live-stream the development process of
an agentic harness capable of playing the full game (and in particular the minimal transformation of
visiontotextnecessarytodoso),seeFigure14foradescriptionofthefinalagentsetup. Assuch,over
the course of the run, modifications were made to the setup as difficulties arose, providing a deeply
interestinglensviawhichtoanalyzesomeofthequalitativeimprovementsthatthe2.5Promodelhas
made, particularly in the regimes of solving long reasoning problems and agentic capabilities over
extended time horizons. Around 1 month later, on May 2, 2025, Gemini 2.5 Pro completed the game
after 813 hours and entered the Hall of Fame to become the Pokémon League Champion! On May
22, 2025, GPP began a fully autonomous 2nd run through the game with Gemini 2.5 Pro (Gemini
2.5 Pro Preview 05-06) with the finalized fixed agentic harness, and progressed through the game
considerablyfaster,completingthegamein406.5hours(nearlyexactlyhalfthetimeofthefirstrun).
16
senotseliM
emaG

|  |  |  |  |
|---|---|---|---|

|  |  | Run 1 |  |
|---|---|---|---|


---

# Page 17

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
See Figure 6 for a timeline of GPP’s progress through major game milestones to game completion.
We report # hours to each milestone in order to normalize for the amount of time models take per
action. See Appendix 8.2 for more figures.
Capabilities assessment
Gemini 2.5 Pro showcased many impressive capabilities associated with reasoning and long-term
planning while playing Pokémon. We will now discuss two in particular, but for more examples, see
Appendix 8.2.
Long Context Agentic Tooling Within the agent scaffolding, GPP has access to two agentic
tools (see Figure 14). These prompted versions of Gemini 2.5 Pro, hereafter pathfinder and
boulder_puzzle_strategist, have been able to:
1. Solve complex spinner puzzles in one shot (for instance in Rocket Hideout),
2. Solve the step-constrained multi-map puzzle of the Safari Zone,
3. Find long pathways through complex mazes like Route 13,
4. Solve boulder puzzles across long distances in Victory Road and the Seafoam Islands.
Eachtaskrequiresreasoningoveralongcontext-thepathfindermodelwouldoftenhavetoreason
over contexts of 100K+ tokens, and find paths up to 50 actions in length (in the extreme case, paths
consisting of up to 150 actions have also been found!).
Long Horizon Task Coherence WhileGemini2.5Proisimpressiveinamorelocalsense,theagent
alsoexhibitedremarkablelong-termtaskcoherenceinachievingglobal,high-levelgoalsinthefaceof
realandhallucinatedsetbackstowardsmakingforwardprogress. Becausetheagentisabletochange
goals at will, and will generally follow those goals as long as needed, it is extremely impressive that
the agent can satisfy numerous requirements for tactical, necessary goals, such as acquiring Hidden
Moves, as well as maintain enough strategic task coherence to beat the entire game and become the
Pokémon Champion.
Where does 2.5 Pro struggle while playing Pokémon?
In addition to more standard hallucination issues (which interestingly were plausibly reduced in Run
2 by explicitly prompting the model to act as a player completely new to the game, see Appendix 8.2
for more details), there are a few particular points of struggle we would like to emphasize.
Screen reading While obtaining excellent benchmark numbers on real-world vision tasks, 2.5 Pro
struggled to utilize the raw pixels of the Game Boy screen directly, though it could occasionally take
cues from information on the pixels. As a result, it was necessary for the required information from
the screen to be translated into a text format in the agent framework, using information from the
game’s RAM state. During one portion of the game, the developer tested an ablation where all vision
was completely removed from the model context – the model was able to function roughly as well
as without the vision information, suggesting that most of the performance does not significantly
depend on the visual input.
Long Context Reasoning Gemini 2.5 Pro’s state-of-the-art long context performance for both
reasoning and retrieval tasks (see Tables 3 and 4) was a cornerstone of the GPP agent’s success. Its
ability to reason over a 100k token context was instrumental for leveraging the complex toolset and
17


---

# Page 18

Gemini2.5:PushingtheFrontierwithAdvancedReasoning,Multimodality,LongContext,andNextGenerationAgenticCapabilities.
maintaining a relatively coherent strategy (e.g., optimal balance of performance, planning quality,
and information recall.)
While Gemini 2.5 Pro supports 1M+ token context, making effective use of it for agents presents
a new research frontier. In this agentic setup, it was observed that as the context grew significantly
beyond 100k tokens, the agent showed a tendency toward favoring repeating actions from its vast
history rather than synthesizing novel plans. This phenomenon, albeit anecdotal, highlights an
important distinction between long-context for retrieval and long-context for multi-step, generative
reasoning.
Teachinganagenttoeffectivelyplanandavoidsuchloopsovermassivepasttrajectoriesofcontext
is an exciting and active area of research; the co-design of agent scaffolds and models to unlock the
full potential of million-token context is an intriguing research direction and one of our primary
focuses.
4.2. What else can Gemini 2.5 do?
Gemini 2.5 Pro excels at transforming diverse, often unstructured, inputs into interactive and func-
tional applications. For instance, it can take a PDF script of a play and generate a tool that allows
drama students to practice their lines. Gemini 2.5 Pro can also take an uploaded photograph of a
bookshelf and create a curated book recommendation application. Gemini 2.5 Pro can utilize its
underlying spatial understanding capability and convert images into a structural representation like
HTML or SVG. In Figure 16 in Appendix 8.4, we show a comparison of Gemini 1.5 Pro and Gemini
2.5Proonanimage-to-svgtask,whereGemini2.5Proreconstructsmuchmorevisualdetailsandthe
spatial arrangements of objects better resembles the original image.
Furthermore, Gemini 2.5 Pro demonstrates strong skills in generating sophisticated simulations
and visualizations, ranging from interactive solar system models (source) to the creative rendering of
abstract mathematical concepts, such as drawing a logo using Fourier series (source). This capability
extendstothedevelopmentoftoolsthatintersectcreativityandutility: weseeexamplesofspecialized
applicationslikeacustomcartographytoolorusecasesthatgeneratephotorealistic3Duserinterfaces
from descriptive text and reference images, complete with appropriate styling and interactivity
(source).
Collectively, these examples illustrate that Gemini 2.5 Pro is not just a useful coding and writing
assistant, but excels at a wide range of complex tasks, ranging from those relevant for education
to creative expression. The model empowers users to rapidly prototype specialized utilities, de-
velop engaging educational content, and realize intricate creative visions with a high degree of
sophistication.
4.3. Gemini in Google Products
As a final example of what Gemini can do, we note that Gemini (or a custom version of Gemini) is
now incorporated into a wide variety of Google products. These include, but are not limited to, AI
Overviews and AI Mode within Google Search, Project Astra, the audiovisual-to-audio dialog agent,
Gemini Deep Research, the research assistant discussed in Section 2.7, NotebookLM, the tool capable
of generating podcasts and audio overviews from even the most obscure inputs, Project Mariner, the
web browsing agent, and Google’s coding agent, Jules.
18


---

