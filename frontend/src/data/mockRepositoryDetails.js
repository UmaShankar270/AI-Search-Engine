// Detailed mock data database for repository details page in Phase 4.
export const mockRepositoryDetails = {
  zustand: {
    id: 1,
    owner: 'pmndrs',
    name: 'zustand',
    avatar: 'https://images.unsplash.com/photo-1618401471353-b98aedd07871?auto=format&fit=crop&w=80&h=80&q=80',
    description: 'Bearish micro-state management library for React. Simple, fast, and un-opinionated API with hooks support.',
    language: 'TypeScript',
    stars: 42300,
    forks: 1350,
    openIssues: 18,
    license: 'MIT',
    lastUpdated: '2026-07-28',
    about: 'Zustand is a small, fast, and scalable bearbones state-management solution. It has a pretty comfy API based on hooks, is not opinionated, and does not wrap your app in providers. It is optimized to avoid render performance bottlenecks and zombie child issues.',
    topics: ['react', 'state-management', 'hooks', 'typescript', 'flux', 'devtools'],
    size: '4.8 MB',
    createdDate: '2019-04-12',
    latestRelease: 'v4.5.2',
    defaultBranch: 'main',
    visibility: 'Public',
    homepageUrl: 'https://zustand.docs.pmnd.rs',
    languages: [
      { name: 'TypeScript', percentage: 98.2, color: '#3178c6' },
      { name: 'JavaScript', percentage: 1.5, color: '#f1e05a' },
      { name: 'CSS', percentage: 0.3, color: '#563d7c' },
    ],
    aiAnalysis: {
      summary: 'Zustand is a state-of-the-art state management engine for React. Unlike Redux or Context, it relies on simple hook closures without provider wrappers, resulting in higher rendering performance and clean code footprint.',
      strengths: [
        'Minimal boilerplate code compared to Redux Toolkit.',
        'High performance: allows subscription selectors to prevent unnecessary component renders.',
        'Does not require App Provider wrapping, making micro-frontend integration trivial.'
      ],
      weaknesses: [
        'Lack of rigid framework guidelines, which can lead to disorganized code on massive teams.',
        'No default cache management or request deduping builtin.'
      ],
      bestUseCases: [
        'Small to mid-scale state synchronization.',
        'React UI components that require high-speed reactive updates.',
        'Dashboard and local widget widgets stores.'
      ],
      scores: {
        maintenance: 95,
        documentation: 92,
        community: 96,
        codeQuality: 98,
        security: 94
      }
    },
    readmeHtml: `
# 🐻 Zustand

Bearish micro-state management library for React.

\`\`\`bash
npm install zustand
\`\`\`

### Quick Start

Create a store with your state and actions:

\`\`\`javascript
import { create } from 'zustand'

const useStore = create((set) => ({
  bears: 0,
  increasePopulation: () => set((state) => ({ bears: state.bears + 1 })),
  removeAllBears: () => set({ bears: 0 }),
}))
\`\`\`

Then bind your components:

\`\`\`javascript
function BearCounter() {
  const bears = useStore((state) => state.bears)
  return <h1>{bears} around here ...</h1>
}

function Controls() {
  const increasePopulation = useStore((state) => state.increasePopulation)
  return <button onClick={increasePopulation}>one up</button>
}
\`\`\`
`,
    contributors: [
      { username: 'dai-shi', contributions: 890, avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'drcmda', contributions: 540, avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'aleclarson', contributions: 120, avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'joshua', contributions: 90, avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=40&h=40&q=80' },
    ],
    activity: {
      commitRate: 92,
      issueCloseRate: 88,
      prMergeRate: 91,
      releaseFrequency: 94
    }
  },
  supabase: {
    id: 3,
    owner: 'supabase',
    name: 'supabase',
    avatar: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=80&h=80&q=80',
    description: 'The open source Firebase alternative. Build production-grade backends with a Postgres database.',
    language: 'TypeScript',
    stars: 68400,
    forks: 5300,
    openIssues: 180,
    license: 'Apache-2.0',
    lastUpdated: '2026-07-29',
    about: 'Supabase is an open source Firebase alternative. We are building the features of Firebase using enterprise-grade open source tools. Supabase provides database, auth, storage, and edge functions with real-time replication.',
    topics: ['postgres', 'firebase-alternative', 'authentication', 'realtime-database', 'storage', 'rest-api'],
    size: '24.1 MB',
    createdDate: '2020-01-15',
    latestRelease: 'v2.45.1',
    defaultBranch: 'master',
    visibility: 'Public',
    homepageUrl: 'https://supabase.com',
    languages: [
      { name: 'TypeScript', percentage: 76.5, color: '#3178c6' },
      { name: 'JavaScript', percentage: 12.0, color: '#f1e05a' },
      { name: 'Go', percentage: 8.5, color: '#00add8' },
      { name: 'PLpgSQL', percentage: 3.0, color: '#dad8a2' },
    ],
    aiAnalysis: {
      summary: 'Supabase is a comprehensive Backend-as-a-Service wrapper built on Postgres. It replaces custom Node/Django database servers with direct client-to-Postgres queries, row-level security policies, and instant OAuth integrations.',
      strengths: [
        'Utilizes actual enterprise-grade Postgres instead of custom NoSQL structures.',
        'Built-in real-time replication and websockets channels.',
        'Extremely active repository releases and feature launches.'
      ],
      weaknesses: [
        'Postgres schemas requires SQL expertise compared to schema-less Firestore databases.',
        'Self-hosting dashboard configuration has a high setup complexity.'
      ],
      bestUseCases: [
        'SaaS platforms needing robust relations and user ownership rules.',
        'Real-time dashboards, chat systems, and live tracking widgets.',
        'Fast hackathon MVP backends.'
      ],
      scores: {
        maintenance: 97,
        documentation: 94,
        community: 98,
        codeQuality: 95,
        security: 93
      }
    },
    readmeHtml: `
# Supabase

The open source Firebase alternative.

\`\`\`bash
npm install @supabase/supabase-js
\`\`\`

### Initialize the SDK

\`\`\`javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://your-project.supabase.co'
const supabaseKey = 'your-anon-key'
const supabase = createClient(supabaseUrl, supabaseKey)
\`\`\`

### Fetch Data

\`\`\`javascript
const { data: users, error } = await supabase
  .from('profiles')
  .select('*')
\`\`\`
`,
    contributors: [
      { username: 'kiwicopple', contributions: 1240, avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'awalias', contributions: 890, avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'soedirgo', contributions: 450, avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=40&h=40&q=80' },
    ],
    activity: {
      commitRate: 98,
      issueCloseRate: 92,
      prMergeRate: 96,
      releaseFrequency: 98
    }
  }
};

// Fallback generator for un-mocked details
export function getGeneratedMockDetails(owner, repo) {
  const slug = repo.toLowerCase();
  if (mockRepositoryDetails[slug]) return mockRepositoryDetails[slug];

  // Dynamic seed stats
  const starsCount = Math.floor(Math.random() * 8000) + 1200;
  const forksCount = Math.floor(starsCount * 0.12);

  return {
    id: Math.floor(Math.random() * 9000) + 1000,
    owner,
    name: repo,
    avatar: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=80&h=80&q=80',
    description: `Dynamic repository presentation folder for ${owner}/${repo}. Ready to consume REST APIs.`,
    language: Math.random() > 0.5 ? 'TypeScript' : 'JavaScript',
    stars: starsCount,
    forks: forksCount,
    openIssues: Math.floor(starsCount * 0.005),
    license: 'MIT',
    lastUpdated: '2026-07-29',
    about: `${repo} is an open source component designed to address modern modular structures. Ideal for scaling developer ecosystems and speeds.`,
    topics: ['react', 'web-app', 'developer-tools', 'open-source'],
    size: '1.8 MB',
    createdDate: '2022-09-11',
    latestRelease: 'v1.0.0',
    defaultBranch: 'main',
    visibility: 'Public',
    homepageUrl: `https://github.com/${owner}/${repo}`,
    languages: [
      { name: 'TypeScript', percentage: 90.0, color: '#3178c6' },
      { name: 'JavaScript', percentage: 10.0, color: '#f1e05a' },
    ],
    aiAnalysis: {
      summary: 'Dynamic AI insights generated by mock parameters. Represents code compliance checks, modular structures, and standard devops release metrics.',
      strengths: [
        'Lightweight build structures.',
        'Accessible primitives support.'
      ],
      weaknesses: [
        'Requires manual backend synchronization configurations.'
      ],
      bestUseCases: [
        'Static website configurations.',
        'Prototype layouts.'
      ],
      scores: {
        maintenance: 85,
        documentation: 80,
        community: 75,
        codeQuality: 88,
        security: 90
      }
    },
    readmeHtml: `
# ${repo}

Dynamic placeholder README.

\`\`\`bash
npm install ${repo}
\`\`\`
`,
    contributors: [
      { username: 'developer-x', contributions: 82, avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=40&h=40&q=80' },
      { username: 'coder-y', contributions: 45, avatar: 'https://images.unsplash.com/photo-1570295999919-56ceb5ecca61?auto=format&fit=crop&w=40&h=40&q=80' },
    ],
    activity: {
      commitRate: 80,
      issueCloseRate: 75,
      prMergeRate: 85,
      releaseFrequency: 70
    }
  };
}
