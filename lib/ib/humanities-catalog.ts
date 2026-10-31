import type { IbCourse, IbCourseLevel, IbSyllabusSubtopic } from "./catalog.ts";

export const HUMANITIES_SUBTOPICS: Record<"economics" | "business-management", Record<string, IbSyllabusSubtopic[]>> = {
  "economics": {
    "introduction": [
      {
        "code": "1.1",
        "title": "What is economics?",
        "additionalHlOnly": false
      },
      {
        "code": "1.2",
        "title": "How do economists approach the world?",
        "additionalHlOnly": false
      }
    ],
    "microeconomics": [
      {
        "code": "2.1",
        "title": "Demand",
        "additionalHlOnly": false
      },
      {
        "code": "2.2",
        "title": "Supply",
        "additionalHlOnly": false
      },
      {
        "code": "2.3",
        "title": "Competitive market equilibrium",
        "additionalHlOnly": false
      },
      {
        "code": "2.4",
        "title": "Critique of maximizing behaviour",
        "additionalHlOnly": true
      },
      {
        "code": "2.5",
        "title": "Elasticity of demand",
        "additionalHlOnly": false
      },
      {
        "code": "2.6",
        "title": "Elasticity of supply",
        "additionalHlOnly": false
      },
      {
        "code": "2.7",
        "title": "Role of government in microeconomics",
        "additionalHlOnly": false
      },
      {
        "code": "2.8",
        "title": "Externalities and common access resources",
        "additionalHlOnly": false
      },
      {
        "code": "2.9",
        "title": "Public goods",
        "additionalHlOnly": false
      },
      {
        "code": "2.10",
        "title": "Asymmetric information",
        "additionalHlOnly": true
      },
      {
        "code": "2.11",
        "title": "Market power",
        "additionalHlOnly": true
      },
      {
        "code": "2.12",
        "title": "The market's inability to achieve equity",
        "additionalHlOnly": true
      }
    ],
    "macroeconomics": [
      {
        "code": "3.1",
        "title": "Measuring economic activity",
        "additionalHlOnly": false
      },
      {
        "code": "3.2",
        "title": "Aggregate demand and aggregate supply",
        "additionalHlOnly": false
      },
      {
        "code": "3.3",
        "title": "Macroeconomic objectives",
        "additionalHlOnly": false
      },
      {
        "code": "3.4",
        "title": "Inequality and poverty",
        "additionalHlOnly": false
      },
      {
        "code": "3.5",
        "title": "Monetary policy",
        "additionalHlOnly": false
      },
      {
        "code": "3.6",
        "title": "Fiscal policy",
        "additionalHlOnly": false
      },
      {
        "code": "3.7",
        "title": "Supply-side policies",
        "additionalHlOnly": false
      }
    ],
    "global-economy": [
      {
        "code": "4.1",
        "title": "Benefits of international trade",
        "additionalHlOnly": false
      },
      {
        "code": "4.2",
        "title": "Types of trade protection",
        "additionalHlOnly": false
      },
      {
        "code": "4.3",
        "title": "Arguments for and against trade protection",
        "additionalHlOnly": false
      },
      {
        "code": "4.4",
        "title": "Economic integration",
        "additionalHlOnly": false
      },
      {
        "code": "4.5",
        "title": "Exchange rates",
        "additionalHlOnly": false
      },
      {
        "code": "4.6",
        "title": "Balance of payments",
        "additionalHlOnly": false
      },
      {
        "code": "4.7",
        "title": "Sustainable development",
        "additionalHlOnly": false
      },
      {
        "code": "4.8",
        "title": "Measuring development",
        "additionalHlOnly": false
      },
      {
        "code": "4.9",
        "title": "Barriers to growth and development",
        "additionalHlOnly": false
      },
      {
        "code": "4.10",
        "title": "Growth and development strategies",
        "additionalHlOnly": false
      }
    ]
  },
  "business-management": {
    "introduction-business": [
      {
        "code": "1.1",
        "title": "What is a business?",
        "additionalHlOnly": false
      },
      {
        "code": "1.2",
        "title": "Types of business entities",
        "additionalHlOnly": false
      },
      {
        "code": "1.3",
        "title": "Business objectives",
        "additionalHlOnly": false
      },
      {
        "code": "1.4",
        "title": "Stakeholders",
        "additionalHlOnly": false
      },
      {
        "code": "1.5",
        "title": "Growth and evolution",
        "additionalHlOnly": false
      },
      {
        "code": "1.6",
        "title": "Multinational companies (MNCs)",
        "additionalHlOnly": false
      }
    ],
    "human-resources": [
      {
        "code": "2.1",
        "title": "Introduction to human resource management",
        "additionalHlOnly": false
      },
      {
        "code": "2.2",
        "title": "Organizational structure",
        "additionalHlOnly": false
      },
      {
        "code": "2.3",
        "title": "Leadership and management",
        "additionalHlOnly": false
      },
      {
        "code": "2.4",
        "title": "Motivation and demotivation",
        "additionalHlOnly": false
      },
      {
        "code": "2.5",
        "title": "Organizational (corporate) culture",
        "additionalHlOnly": true
      },
      {
        "code": "2.6",
        "title": "Communication",
        "additionalHlOnly": false
      },
      {
        "code": "2.7",
        "title": "Industrial/employee relations",
        "additionalHlOnly": true
      }
    ],
    "finance-accounts": [
      {
        "code": "3.1",
        "title": "Introduction to finance",
        "additionalHlOnly": false
      },
      {
        "code": "3.2",
        "title": "Sources of finance",
        "additionalHlOnly": false
      },
      {
        "code": "3.3",
        "title": "Costs and revenues",
        "additionalHlOnly": false
      },
      {
        "code": "3.4",
        "title": "Final accounts",
        "additionalHlOnly": false
      },
      {
        "code": "3.5",
        "title": "Profitability and liquidity ratio analysis",
        "additionalHlOnly": false
      },
      {
        "code": "3.6",
        "title": "Efficiency ratio analysis",
        "additionalHlOnly": true
      },
      {
        "code": "3.7",
        "title": "Cash flow",
        "additionalHlOnly": false
      },
      {
        "code": "3.8",
        "title": "Investment appraisal",
        "additionalHlOnly": false
      },
      {
        "code": "3.9",
        "title": "Budgets",
        "additionalHlOnly": true
      }
    ],
    "marketing": [
      {
        "code": "4.1",
        "title": "Introduction to marketing",
        "additionalHlOnly": false
      },
      {
        "code": "4.2",
        "title": "Marketing planning",
        "additionalHlOnly": false
      },
      {
        "code": "4.3",
        "title": "Sales forecasting",
        "additionalHlOnly": true
      },
      {
        "code": "4.4",
        "title": "Market research",
        "additionalHlOnly": false
      },
      {
        "code": "4.5",
        "title": "The seven Ps of the marketing mix",
        "additionalHlOnly": false
      },
      {
        "code": "4.6",
        "title": "International marketing",
        "additionalHlOnly": true
      }
    ],
    "operations-management": [
      {
        "code": "5.1",
        "title": "Introduction to operations management",
        "additionalHlOnly": false
      },
      {
        "code": "5.2",
        "title": "Operations methods",
        "additionalHlOnly": false
      },
      {
        "code": "5.3",
        "title": "Lean production and quality management",
        "additionalHlOnly": true
      },
      {
        "code": "5.4",
        "title": "Location",
        "additionalHlOnly": false
      },
      {
        "code": "5.5",
        "title": "Break-even analysis",
        "additionalHlOnly": false
      },
      {
        "code": "5.6",
        "title": "Production planning",
        "additionalHlOnly": true
      },
      {
        "code": "5.7",
        "title": "Crisis management and contingency planning",
        "additionalHlOnly": true
      },
      {
        "code": "5.8",
        "title": "Research and development",
        "additionalHlOnly": true
      },
      {
        "code": "5.9",
        "title": "Management information systems",
        "additionalHlOnly": true
      }
    ]
  }
};

export const HUMANITIES_COURSES: Record<"economics" | "business-management", IbCourse> = {
  "economics": {
    "id": "economics",
    "label": "Economics",
    "title": "Economics",
    "subtitle": "Diploma Programme",
    "symbol": "↗",
    "topics": [
      {
        "id": "introduction",
        "code": "1",
        "title": "Introduction to economics",
        "description": "Explore introduction to economics through original case studies, data and evaluation.",
        "subtopics": [
          "What is economics?",
          "How do economists approach the world?"
        ]
      },
      {
        "id": "microeconomics",
        "code": "2",
        "title": "Microeconomics",
        "description": "Explore microeconomics through original case studies, data and evaluation.",
        "subtopics": [
          "Demand",
          "Supply",
          "Competitive market equilibrium",
          "Critique of maximizing behaviour",
          "Elasticity of demand",
          "Elasticity of supply",
          "Role of government in microeconomics",
          "Externalities and common access resources",
          "Public goods",
          "Asymmetric information",
          "Market power",
          "The market's inability to achieve equity"
        ]
      },
      {
        "id": "macroeconomics",
        "code": "3",
        "title": "Macroeconomics",
        "description": "Explore macroeconomics through original case studies, data and evaluation.",
        "subtopics": [
          "Measuring economic activity",
          "Aggregate demand and aggregate supply",
          "Macroeconomic objectives",
          "Inequality and poverty",
          "Monetary policy",
          "Fiscal policy",
          "Supply-side policies"
        ]
      },
      {
        "id": "global-economy",
        "code": "4",
        "title": "The global economy",
        "description": "Explore the global economy through original case studies, data and evaluation.",
        "subtopics": [
          "Benefits of international trade",
          "Types of trade protection",
          "Arguments for and against trade protection",
          "Economic integration",
          "Exchange rates",
          "Balance of payments",
          "Sustainable development",
          "Measuring development",
          "Barriers to growth and development",
          "Growth and development strategies"
        ]
      }
    ]
  },
  "business-management": {
    "id": "business-management",
    "label": "Business management",
    "title": "Business management",
    "subtitle": "Diploma Programme",
    "symbol": "◈",
    "topics": [
      {
        "id": "introduction-business",
        "code": "1",
        "title": "Introduction to business management",
        "description": "Explore introduction to business management through original case studies, data and evaluation.",
        "subtopics": [
          "What is a business?",
          "Types of business entities",
          "Business objectives",
          "Stakeholders",
          "Growth and evolution",
          "Multinational companies"
        ]
      },
      {
        "id": "human-resources",
        "code": "2",
        "title": "Human resource management",
        "description": "Explore human resource management through original case studies, data and evaluation.",
        "subtopics": [
          "Introduction to human resource management",
          "Organizational structure",
          "Leadership and management",
          "Motivation and demotivation",
          "Organizational culture",
          "Communication",
          "Industrial and employee relations"
        ]
      },
      {
        "id": "finance-accounts",
        "code": "3",
        "title": "Finance and accounts",
        "description": "Explore finance and accounts through original case studies, data and evaluation.",
        "subtopics": [
          "Introduction to finance",
          "Sources of finance",
          "Costs and revenues",
          "Final accounts",
          "Profitability and liquidity ratio analysis",
          "Efficiency ratio analysis",
          "Cash flow",
          "Investment appraisal",
          "Budgets"
        ]
      },
      {
        "id": "marketing",
        "code": "4",
        "title": "Marketing",
        "description": "Explore marketing through original case studies, data and evaluation.",
        "subtopics": [
          "Introduction to marketing",
          "Marketing planning",
          "Sales forecasting",
          "Market research",
          "The marketing mix",
          "International marketing"
        ]
      },
      {
        "id": "operations-management",
        "code": "5",
        "title": "Operations management",
        "description": "Explore operations management through original case studies, data and evaluation.",
        "subtopics": [
          "Introduction to operations management",
          "Operations methods",
          "Lean production and quality management",
          "Location",
          "Break-even analysis",
          "Production planning",
          "Crisis management and contingency planning",
          "Research and development",
          "Management information systems"
        ]
      }
    ]
  }
};

export function humanitiesSyllabusSubtopics(subject: "economics" | "business-management", topicId?: string, course: IbCourseLevel = "hl"): IbSyllabusSubtopic[] {
 return Object.entries(HUMANITIES_SUBTOPICS[subject]).filter(([id]) => !topicId || id === topicId).flatMap(([, values]) => values).filter(item => course === "hl" || !item.additionalHlOnly);
}
