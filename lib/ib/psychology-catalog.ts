import type { IbCourse, IbCourseLevel, IbSyllabusSubtopic } from "./catalog.ts";

/** First assessment 2027. The grouping codes below are internal, not IB outcome numbers. */
export const PSYCHOLOGY_FIRST_ASSESSMENT = 2027;
export const PSYCHOLOGY_BAND_RANGES = {
  3: [[0, 0], [1, 1], [2, 2], [3, 3]],
  4: [[0, 0], [1, 2], [3, 4]],
  6: [[0, 0], [1, 2], [3, 4], [5, 6]],
  15: [[0, 0], [1, 3], [4, 6], [7, 9], [10, 12], [13, 15]],
} as const;
export const PSYCHOLOGY_CODE_NOTE = "Internal Thriving Scholars content-grouping codes; not official IB syllabus numbering.";
export const PSYCHOLOGY_CONTEXTS = ["general", "health-wellbeing", "human-development", "human-relationships", "learning-cognition"] as const;
export const PSYCHOLOGY_CONCEPTS = ["bias", "causality", "change", "measurement", "perspective", "responsibility"] as const;
export const PSYCHOLOGY_TOPICS = [
  {
    "id": "biological-approach",
    "token": "bio",
    "code": "BIO",
    "title": "Biological approach",
    "description": "Biological explanations of behaviour, brain function and inheritance.",
    "additionalHlOnly": false,
    "questions": 40,
    "subtopics": [
      {
        "code": "BIO.01",
        "title": "Animal models and research",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.02",
        "title": "Biological reductionism",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.03",
        "title": "Brain imaging techniques",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.04",
        "title": "Chemical messengers",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.05",
        "title": "Diathesis-stress model",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.06",
        "title": "Genetic inheritance",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.07",
        "title": "Localization of function",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.08",
        "title": "Neuroplasticity",
        "additionalHlOnly": false
      },
      {
        "code": "BIO.09",
        "title": "Neurotransmission",
        "additionalHlOnly": false
      }
    ]
  },
  {
    "id": "cognitive-approach",
    "token": "cog",
    "code": "COG",
    "title": "Cognitive approach",
    "description": "Thinking, learning, memory and cognitive explanations of behaviour.",
    "additionalHlOnly": false,
    "questions": 40,
    "subtopics": [
      {
        "code": "COG.01",
        "title": "Anchoring bias",
        "additionalHlOnly": false
      },
      {
        "code": "COG.02",
        "title": "Classical conditioning",
        "additionalHlOnly": false
      },
      {
        "code": "COG.03",
        "title": "Cognitive load theory",
        "additionalHlOnly": false
      },
      {
        "code": "COG.04",
        "title": "Cognitive models",
        "additionalHlOnly": false
      },
      {
        "code": "COG.05",
        "title": "Confirmation bias",
        "additionalHlOnly": false
      },
      {
        "code": "COG.06",
        "title": "Dual processing theory",
        "additionalHlOnly": false
      },
      {
        "code": "COG.07",
        "title": "Operant conditioning",
        "additionalHlOnly": false
      },
      {
        "code": "COG.08",
        "title": "Schema theory",
        "additionalHlOnly": false
      }
    ]
  },
  {
    "id": "sociocultural-approach",
    "token": "soc",
    "code": "SOC",
    "title": "Sociocultural approach",
    "description": "Social identity, cultural influences and interpersonal behaviour.",
    "additionalHlOnly": false,
    "questions": 40,
    "subtopics": [
      {
        "code": "SOC.01",
        "title": "Cognitive dissonance",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.02",
        "title": "Compliance techniques",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.03",
        "title": "Conformity",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.04",
        "title": "Cultural dimensions",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.05",
        "title": "Emic approach",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.06",
        "title": "Enculturation",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.07",
        "title": "Etic approach",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.08",
        "title": "Models of acculturation",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.09",
        "title": "Social identity theory",
        "additionalHlOnly": false
      },
      {
        "code": "SOC.10",
        "title": "Social learning theory",
        "additionalHlOnly": false
      }
    ]
  },
  {
    "id": "research-methodology",
    "token": "res",
    "code": "RES",
    "title": "Research methodology",
    "description": "Research designs, ethics, sampling and evaluation of psychological evidence.",
    "additionalHlOnly": false,
    "questions": 60,
    "subtopics": [
      {
        "code": "RES.01",
        "title": "Research methods",
        "additionalHlOnly": false
      },
      {
        "code": "RES.02",
        "title": "Sampling techniques",
        "additionalHlOnly": false
      },
      {
        "code": "RES.03",
        "title": "Research designs and control",
        "additionalHlOnly": false
      },
      {
        "code": "RES.04",
        "title": "Ethics and researcher responsibility",
        "additionalHlOnly": false
      },
      {
        "code": "RES.05",
        "title": "Measurement, validity and reliability",
        "additionalHlOnly": false
      },
      {
        "code": "RES.06",
        "title": "Qualitative research considerations",
        "additionalHlOnly": false
      },
      {
        "code": "RES.07",
        "title": "Comparing class-practical methods",
        "additionalHlOnly": false
      },
      {
        "code": "RES.08",
        "title": "Designing class-practical methods",
        "additionalHlOnly": false
      }
    ]
  },
  {
    "id": "culture",
    "token": "cul",
    "code": "CUL",
    "title": "Culture",
    "description": "Culture and the interpretation of psychological research across contexts.",
    "additionalHlOnly": true,
    "questions": 20,
    "subtopics": [
      {
        "code": "CUL.01",
        "title": "Health and well-being",
        "additionalHlOnly": true
      },
      {
        "code": "CUL.02",
        "title": "Human development",
        "additionalHlOnly": true
      },
      {
        "code": "CUL.03",
        "title": "Human relationships",
        "additionalHlOnly": true
      },
      {
        "code": "CUL.04",
        "title": "Learning and cognition",
        "additionalHlOnly": true
      }
    ]
  },
  {
    "id": "motivation",
    "token": "mot",
    "code": "MOT",
    "title": "Motivation",
    "description": "Motivation, behaviour and evaluation of psychological evidence.",
    "additionalHlOnly": true,
    "questions": 20,
    "subtopics": [
      {
        "code": "MOT.01",
        "title": "Health and well-being",
        "additionalHlOnly": true
      },
      {
        "code": "MOT.02",
        "title": "Human development",
        "additionalHlOnly": true
      },
      {
        "code": "MOT.03",
        "title": "Human relationships",
        "additionalHlOnly": true
      },
      {
        "code": "MOT.04",
        "title": "Learning and cognition",
        "additionalHlOnly": true
      }
    ]
  },
  {
    "id": "technology",
    "token": "tec",
    "code": "TEC",
    "title": "Technology",
    "description": "Technology and psychological research across the four contexts.",
    "additionalHlOnly": true,
    "questions": 20,
    "subtopics": [
      {
        "code": "TEC.01",
        "title": "Health and well-being",
        "additionalHlOnly": true
      },
      {
        "code": "TEC.02",
        "title": "Human development",
        "additionalHlOnly": true
      },
      {
        "code": "TEC.03",
        "title": "Human relationships",
        "additionalHlOnly": true
      },
      {
        "code": "TEC.04",
        "title": "Learning and cognition",
        "additionalHlOnly": true
      }
    ]
  }
] as const;
export const PSYCHOLOGY_SECTIONS = {
  "p1-a": {
    "paper": "paper-1",
    "marks": 4,
    "questionType": "short-response",
    "label": "Paper 1 \u00b7 Section A"
  },
  "p1-b": {
    "paper": "paper-1",
    "marks": 6,
    "questionType": "scenario-response",
    "label": "Paper 1 \u00b7 Section B"
  },
  "p1-c": {
    "paper": "paper-1",
    "marks": 15,
    "questionType": "extended-response",
    "label": "Paper 1 \u00b7 Section C"
  },
  "p2-a-knowledge": {
    "paper": "paper-2",
    "marks": 4,
    "questionType": "research-methods",
    "label": "Paper 2 \u00b7 A: Knowledge"
  },
  "p2-a-application": {
    "paper": "paper-2",
    "marks": 4,
    "questionType": "research-methods",
    "label": "Paper 2 \u00b7 A: Application"
  },
  "p2-a-comparison": {
    "paper": "paper-2",
    "marks": 6,
    "questionType": "research-methods",
    "label": "Paper 2 \u00b7 A: Comparison"
  },
  "p2-a-design": {
    "paper": "paper-2",
    "marks": 6,
    "questionType": "research-methods",
    "label": "Paper 2 \u00b7 A: Design"
  },
  "p2-b": {
    "paper": "paper-2",
    "marks": 15,
    "questionType": "extended-response",
    "label": "Paper 2 \u00b7 Section B"
  },
  "p3-graph": {
    "paper": "paper-3",
    "marks": 3,
    "questionType": "data-response",
    "label": "Paper 3 \u00b7 Graph"
  },
  "p3-data": {
    "paper": "paper-3",
    "marks": 6,
    "questionType": "data-response",
    "label": "Paper 3 \u00b7 Data"
  },
  "p3-qualitative": {
    "paper": "paper-3",
    "marks": 6,
    "questionType": "data-response",
    "label": "Paper 3 \u00b7 Qualitative"
  },
  "p3-synthesis": {
    "paper": "paper-3",
    "marks": 15,
    "questionType": "extended-response",
    "label": "Paper 3 \u00b7 Synthesis"
  }
} as const;

export function psychologyTopic(topicId: string) { return PSYCHOLOGY_TOPICS.find(topic => topic.id === topicId); }
export function psychologyTopicVisible(topicId: string, course: IbCourseLevel = "hl") {
  const topic = psychologyTopic(topicId);
  return !!topic && (course === "hl" || !topic.additionalHlOnly);
}
export function psychologySyllabusSubtopics(topicId?: string, course: IbCourseLevel = "hl"): IbSyllabusSubtopic[] {
  return PSYCHOLOGY_TOPICS.filter(topic => (!topicId || topic.id === topicId) && psychologyTopicVisible(topic.id, course))
    .flatMap(topic => topic.subtopics.map(area => ({ ...area })));
}
export function psychologyPaperStyles(course: IbCourseLevel = "hl", topicId?: string): ("paper-1" | "paper-2" | "paper-3")[] {
  const topic = topicId ? psychologyTopic(topicId) : undefined;
  if (topic?.additionalHlOnly) return course === "hl" ? ["paper-3"] : [];
  return !topic && course === "hl" ? ["paper-1", "paper-2", "paper-3"] : ["paper-1", "paper-2"];
}
export const PSYCHOLOGY_COLLECTIONS = PSYCHOLOGY_TOPICS.map(topic => ({
  id: `psychology-${topic.id}` as const, subject: "psychology" as const, topicId: topic.id,
  code: topic.code, title: topic.title, description: topic.description,
}));
export const PSYCHOLOGY_COURSE: IbCourse = {
  id: "psychology", label: "Psychology", title: "Psychology", subtitle: "Diploma Programme · First assessment 2027", symbol: "Ψ", firstAssessment: PSYCHOLOGY_FIRST_ASSESSMENT,
  topics: PSYCHOLOGY_TOPICS.map(topic => ({ id: topic.id, code: topic.code, title: topic.title, description: topic.description, subtopics: topic.subtopics.map(area => area.title) })),
};
