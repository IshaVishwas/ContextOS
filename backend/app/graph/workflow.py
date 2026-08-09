from langgraph.graph import StateGraph, START, END
from app.graph.state import ContextOSState
from app.graph.nodes import (
    retrieve_and_adapt_node,
    rank_cam_node,
    compress_scc_node,
    compile_apc_node,
    execute_llm_node,
    record_evaluation_node
)

def create_contextos_graph():
    workflow = StateGraph(ContextOSState)

    # Add nodes representing existing ContextOS pipeline components
    workflow.add_node("retrieve_and_adapt", retrieve_and_adapt_node)
    workflow.add_node("rank_cam", rank_cam_node)
    workflow.add_node("compress_scc", compress_scc_node)
    workflow.add_node("compile_apc", compile_apc_node)
    workflow.add_node("execute_llm", execute_llm_node)
    workflow.add_node("record_evaluation", record_evaluation_node)

    # Link pipeline graph
    workflow.add_edge(START, "retrieve_and_adapt")
    workflow.add_edge("retrieve_and_adapt", "rank_cam")
    workflow.add_edge("rank_cam", "compress_scc")
    workflow.add_edge("compress_scc", "compile_apc")
    workflow.add_edge("compile_apc", "execute_llm")
    workflow.add_edge("execute_llm", "record_evaluation")
    workflow.add_edge("record_evaluation", END)

    return workflow.compile()

contextos_graph = create_contextos_graph()
