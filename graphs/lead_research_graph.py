from langgraph.graph import (
    StateGraph,
    END
)

from graphs.state import (
    LeadResearchState
)

from agents import (
    RequirementAgent,
    ApolloAgent,
    LinkedInAgent,
    ValidationAgent,
    EmailAgent,
    ContactAgent,
    CompanyAgent,
    RevenueAgent,
    QualityAgent,
    HumanReviewAgent
)


def build_graph():

    graph = StateGraph(
        LeadResearchState
    )


    # Create agents
    requirement = RequirementAgent()
    apollo = ApolloAgent()
    linkedin = LinkedInAgent()
    validation = ValidationAgent()
    email = EmailAgent()
    contact = ContactAgent()
    company = CompanyAgent()
    revenue = RevenueAgent()
    quality = QualityAgent()
    human = HumanReviewAgent()


    # Add nodes
    graph.add_node(
        "requirement",
        requirement.execute
    )

    graph.add_node(
        "apollo",
        apollo.execute
    )

    graph.add_node(
        "linkedin",
        linkedin.execute
    )

    graph.add_node(
        "validation",
        validation.execute
    )

    graph.add_node(
        "email",
        email.execute
    )

    graph.add_node(
        "company",
        company.execute
    )

    graph.add_node(
        "contact",
        contact.execute
    )

    graph.add_node(
        "revenue",
        revenue.execute
    )

    graph.add_node(
        "quality",
        quality.execute
    )

    graph.add_node(
        "human_review",
        human.execute
    )


    # Entry point
    graph.set_entry_point(
        "requirement"
    )


    # Main flow — LinkedIn Sales Navigator searches first, Apollo fills gaps
    graph.add_edge(
        "requirement",
        "linkedin"
    )

    graph.add_edge(
        "linkedin",
        "apollo"
    )

    graph.add_edge(
        "apollo",
        "validation"
    )


    # Enrichment (linear — contact depends on email_leads)
    graph.add_edge("validation", "email")
    graph.add_edge("email", "contact")
    graph.add_edge("contact", "company")


    graph.add_edge("company", "revenue")

    graph.add_edge(
        "revenue",
        "quality"
    )

    graph.add_edge(
        "quality",
        "human_review"
    )


    graph.add_edge(
        "human_review",
        END
    )


    return graph.compile(), linkedin