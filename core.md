Voice Agent Widget — Production README
1️⃣ Project Overview

The Voice Agent Widget is a production-grade, embeddable conversational interface designed to function as an AI employee on client websites. It enables visitors to interact with businesses through voice-only dialogue, receiving spoken responses grounded exclusively in structured company knowledge stored within the client’s dedicated backend environment.

The system is built as a SaaS platform supporting multiple client deployments, where each client operates within an isolated backend infrastructure, ensuring strict data separation, brand customization, and knowledge scoping.

2️⃣ Core Product Objective

Deliver a floating AI employee widget that:

Introduces itself upon activation

Listens to visitor voice queries

Retrieves answers from company knowledge

Responds in spoken voice

Supports follow-up dialogue

Logs conversations for analytics

Operates within isolated client environments

3️⃣ Widget Experience Design
Floating AI Avatar

The widget appears as a floating AI employee avatar positioned at the bottom corner of the client’s webpage.

The avatar represents a virtual staff member and visually reflects the client’s brand identity.

Each client can customize:

Avatar image

Persona styling

Brand alignment

Activation Behavior

When a visitor clicks the widget:

The voice panel activates

The agent plays a spoken introduction

Listening mode begins automatically

No additional buttons are required to start speaking.

4️⃣ Introduction Interaction

The introduction message plays every time the widget is opened.

Configured via admin dashboard.

Example structure:

Agent identity

Company representation

Assistance scope

Purpose:

Orient visitor

Build trust

Explain capabilities

5️⃣ Voice Interaction Model

The system operates as a strictly voice-only conversational assistant.

Interaction flow

Intro plays

Agent listens automatically

User speaks query

Silence detection ends recording

Backend processes request

Voice response plays

No typing interface is present.

6️⃣ Speech Processing Lifecycle
Step 1 — Voice Capture

Microphone permission requested

Audio recorded

Background noise handled

Silence detection applied

Step 2 — Backend Transmission

Audio securely transmitted to client backend.

Includes:

Session ID

Tenant context

Audio payload

Step 3 — Speech Understanding

Backend converts speech to text and interprets user intent.

7️⃣ Knowledge Retrieval System

The agent is grounded in structured company knowledge stored in the backend.

Knowledge is informational, not transactional.

Supported knowledge categories

Company overview

Services

Products

Pricing

FAQs

Policies

Contact details

Locations

Business hours

Knowledge ingestion

Managed via admin dashboard forms.

Admins can:

Add

Edit

Remove

Organize company data

8️⃣ Static Knowledge Scope

The agent operates only on static company information.

It does not perform live database actions such as:

Order lookups

Bookings

Account updates

Support ticket creation

It functions as an informational AI receptionist.

9️⃣ Response Generation Behavior

Responses must be:

Concise

Conversational

Voice-optimized

Context-aware

The agent should summarize knowledge instead of reading raw data.

Follow-up questioning

The agent can ask clarification questions when helpful.

Example:

“Would you like to know about pricing or features?”

🔟 Hallucination Prevention

The agent must never fabricate information.

If knowledge is unavailable:

Respond transparently

Offer support alternatives

Example:

“I’m not sure about that, but you can contact our support team.”

1️⃣1️⃣ Multi-Language Support

The system supports multilingual voice interaction.

Capabilities include:

Language detection

Configured language sets

Multilingual knowledge mapping

Responses must match visitor language when data is available.

1️⃣2️⃣ Client Isolation Architecture

Each client deployment runs on a separate backend environment.

Isolation includes

Dedicated backend services

Dedicated database

Dedicated knowledge base

Dedicated analytics logs

Dedicated configuration layer

No shared knowledge across clients.

1️⃣3️⃣ Tenant Customization Layer

Each client can configure their voice agent through an admin dashboard.

Customizable elements

Voice tone and speaking style

Avatar image

Introduction script

Brand colors

Widget styling

Supported languages

This enables full brand alignment.

1️⃣4️⃣ Conversation Logging

All interactions are logged within the client’s isolated backend.

Logged data

Voice transcripts

AI responses

Session timestamps

Interaction frequency

Used for analytics and optimization.

1️⃣5️⃣ Analytics Dashboard

Clients can access usage insights including:

Visitor engagement rates

Most asked questions

Conversation volumes

Interaction durations

Helps improve knowledge coverage.

1️⃣6️⃣ Security & Privacy

Voice data handling must ensure:

Secure transmission

Isolated storage

Tenant scoping

Controlled retention

Admins define data retention policies.

1️⃣7️⃣ Widget Performance Requirements

The widget must:

Load asynchronously

Avoid blocking page render

Maintain lightweight footprint

Operate smoothly across browsers

1️⃣8️⃣ Mobile Responsiveness

Widget must function across:

Mobile browsers

Tablets

Desktop screens

UI adapts to screen size while preserving voice usability.

1️⃣9️⃣ Stop Interaction Control

If user taps widget again during:

Listening

Processing

Speaking

The agent must:

Stop recording/playback

Minimize interface

Return to idle state

2️⃣0️⃣ Containerized Deployment (Docker)

The entire system is containerized for deployment portability.

Per-client container stack

Each client deployment includes:

Voice processing backend

Knowledge services

Analytics logging layer

Configuration modules

Containers run independently.

Benefits

Environment consistency

Easy scaling

Infrastructure isolation

Deployment portability

2️⃣1️⃣ Database Architecture

Each container connects only to its dedicated database instance.

Ensures:

Knowledge isolation

Query performance

Data security

2️⃣2️⃣ Scalability Model

Supports multi-client SaaS expansion through:

Independent container deployments

Client-specific backend routing

Horizontal scaling capability

2️⃣3️⃣ Extensibility Roadmap

The architecture is designed for future upgrades including:

Realtime conversational voice

Transactional workflows

CRM integrations

Telephony voice agents

Without redesigning the widget.

🏁 Final Outcome

The system delivers:

A floating AI employee widget

Automatic spoken introductions

Voice-only visitor interaction

Knowledge-grounded responses

Follow-up dialogue capability

Client analytics visibility

Full brand customization

Isolated backend deployments





SpeechSynthesisUtterance output




**Pipeline with Method A**
SpeechSynthesisUtterance plays
        ↓
Web Audio API analyzes volume
        ↓
Mouth opens/closes based on peaks



**Mouth sprites URLS**
https://codelessai.in/ai.png -- base image of avatar
https://codelessai.in/slight-o.png -- image of avatar with mouth slight open
https://codelessai.in/medium-o.png  --image of avatar with mouth medium open
https://codelessai.in/half-o.png -- image of avatar with mouth half open
https://codelessai.in/whalf-o.png  -- image of avatar with mouth widely half open
https://codelessai.in/hhalf-o.png  -- image of avatar with mouth highly half open