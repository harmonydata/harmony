import sys
from typing import List

import numpy as np
from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

from harmony.matching.default_matcher import convert_texts_to_vector

# import matplotlib, tkinter and networkx for the GUI
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.axes import Axes
    import tkinter as tk
    import tkinter.simpledialog
    from tkinter import ttk
    import networkx as nx
    from networkx.algorithms import community
except ImportError as e:
    print("Make sure matplotlib, tkinter and networkx are installed.")
    print(e.msg)
    sys.exit(1)


def draw_cosine_similarity_matrix(questions: List[str], ax: Axes, canvas: FigureCanvasTkAgg):
    """
        Draws a heatmap of the cosine similarity matrix based on the given questions.

        Args:
            questions: List of question strings to visualize
            ax: Matplotlib Axes object to draw on
            canvas: Tkinter canvas for displaying the plot
    """
    embedding_matrix = convert_texts_to_vector(questions)
    similarity_matrix = cosine_similarity(embedding_matrix)

    ax.clear()
    ax.axis("on")
    ax.tick_params(
        axis="both",
        which="both",
        bottom=True,
        left=True,
        labelbottom=True,
        labelleft=True
    )
    ax.set_title("Cosine Similarity Matrix")

    ax.imshow(similarity_matrix, cmap="Blues", interpolation="nearest")
    ax.invert_yaxis()
    canvas.draw()


def draw_clusters_scatter_plot(questions: List[str], ax: Axes, canvas: FigureCanvasTkAgg):
    """
        Draws a scatter plot based on the given questions.
        Uses K-Means clustering for small datasets (<30 questions) and Affinity Propagation clustering for larger ones.

        Args:
            questions: List of question strings to visualize
            ax: Matplotlib Axes object to draw on
            canvas: Tkinter canvas for displaying the plot
    """
    embedding_matrix = convert_texts_to_vector(questions)

    if len(questions) < 30:
        clustering = KMeans(n_clusters=5)
        labels = clustering.fit_predict(embedding_matrix)

        title = "K-Means Clustering"
    else:
        item_to_item_similarity_matrix = np.array(cosine_similarity(embedding_matrix)).astype(np.float64)

        clustering = AffinityPropagation(affinity="precomputed", damping=0.7, random_state=1, max_iter=200,
                                         convergence_iter=15)
        clustering.fit(np.abs(item_to_item_similarity_matrix))
        labels = clustering.labels_

        title = "Affinity Propagation Clustering"

    ax.clear()
    ax.axis("on")
    ax.tick_params(
        axis="both",
        which="both",
        bottom=True,
        left=True,
        labelbottom=True,
        labelleft=True
    )
    ax.set_aspect("auto")
    ax.set_title(title)

    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embedding_matrix)

    ax.scatter(
        reduced_embeddings[:, 0],
        reduced_embeddings[:, 1],
        c=labels,
        cmap="viridis",
        s=100
    )

    for i, point in enumerate(reduced_embeddings):
        ax.annotate(
            str(i),
            xy=(point[0], point[1]),
            xytext=(8, -10),
            textcoords="offset points",
            fontsize=8,
            color="black",
            ha="center"
        )

    canvas.draw()


def draw_network_graph(questions: List[str], ax: Axes, canvas: FigureCanvasTkAgg):
    """
        Draws a network graph based on the given questions, where edges represent high similarity (>0.5).
        Communities are detected using greedy modularity optimization.

        Args:
            questions: List of question strings to visualize
            ax: Matplotlib Axes object to draw on
            canvas: Tkinter canvas for displaying the plot
    """
    embedding_matrix = convert_texts_to_vector(questions)
    similarity_matrix = cosine_similarity(embedding_matrix)

    ax.clear()
    ax.axis("off")
    ax.set_aspect("auto")
    ax.set_title("Network Cluster Graph")

    G = nx.Graph()
    n = similarity_matrix.shape[0]

    i = 0
    for i in range(n):
        for j in range(i + 1, n):
            if similarity_matrix[i, j] > 0.5:
                G.add_edge(i, j, weight=similarity_matrix[i, j])

    communities = list(community.greedy_modularity_communities(G))

    # assign colors to nodes based on communities
    node_color = []
    for comm_idx, comm in enumerate(communities):
        for _ in comm:
            node_color.append(comm_idx)

    # improve node positions using existing layouts
    pos = nx.kamada_kawai_layout(G, weight="weight")
    pos = nx.spring_layout(
        G,
        pos=pos,
        k=2,
        scale=2.0,
        iterations=200
    )

    nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_size=300,
        node_color=node_color,
    )

    nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        width=1.0,
        alpha=0.7
    )

    nx.draw_networkx_labels(
        G, pos,
        ax=ax,
        font_size=12
    )

    canvas.draw()


def setup_gui(questions: List[str]):
    """
        Sets up the Tkinter GUI.

        Args:
            questions: List of question strings to visualize.
    """

    def add_question(questions: List[str], ax: Axes, canvas: FigureCanvasTkAgg):
        """Handles adding new questions through a simple dialog and updates the canvas"""
        question = tkinter.simpledialog.askstring("Add a New Question", "New Question:")
        if question:
            questions.append(question)
            # redraw cosine similarity matrix including newly added question
            draw_cosine_similarity_matrix(questions, ax, canvas)

    def display_questions():
        """Displays all questions in a scrollable dialog window"""
        dialog = tk.Toplevel(root)
        dialog.title("All Questions")
        dialog.geometry("400x600")

        # make the dialog window modal
        dialog.grab_set()
        dialog.focus_set()
        root.attributes("-disabled", True)

        scrollbar = ttk.Scrollbar(dialog)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        questions_text = tk.Text(dialog, height=8)
        questions_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, )

        questions_text["yscrollcommand"] = scrollbar.set
        scrollbar.config(command=questions_text.yview)

        for i, question in enumerate(questions):
            questions_text.insert(tk.END, f"Q{i}: {question}\n")

        def close_dialog():
            """Cleanup when closing the dialog"""
            root.attributes("-disabled", False)
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        dialog.transient(root)
        dialog.wait_window()

    # main window
    root = tk.Tk()
    root.title("Harmony Visualizer")
    root.geometry("800x450")

    # main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # left frame for graphs
    graph_frame = tk.Frame(main_frame, width=350, height=350, bg="white")
    graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    graph_frame.pack_propagate(False)

    # upper right frame for graph buttons
    button_frame = tk.Frame(main_frame, width=200, bg="lightgray")
    button_frame.pack(side=tk.RIGHT, fill=tk.Y)
    # lower right frame with buttons for displaying and adding questions
    bottom_button_frame = tk.Frame(button_frame, bg="lightgray")
    bottom_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    fig, ax = plt.subplots()
    ax.axis("off")  # hide placeholder chart until a button is pressed
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    # the graph buttons and their corresponding draw functions
    button_texts = ["Cosine Similarity Matrix", "Cluster Scatter Plot", "Network Graph"]
    button_functions = [draw_cosine_similarity_matrix, draw_clusters_scatter_plot, draw_network_graph]

    for button_text, function in zip(button_texts, button_functions):
        new_button = tk.Button(button_frame, text=button_text,
                               command=lambda func=function: func(questions, ax, canvas))
        new_button.pack(pady=8, padx=10, fill=tk.X)

    # buttons for adding and displaying questions
    add_question_button = tk.Button(bottom_button_frame, text="Add Question",
                                    command=lambda func=add_question: func(questions, ax, canvas))
    display_questions_button = tk.Button(bottom_button_frame, text="See Questions", command=display_questions)
    add_question_button.pack(pady=8, padx=10, fill=tk.X)
    display_questions_button.pack(pady=8, padx=10, fill=tk.X)

    root.protocol("WM_DELETE_WINDOW", lambda: (plt.close("all"), root.destroy()))
    root.mainloop()


def visualize_questions(questions: List[str]):
    """
        Entry point for the GUI.

        Args:
            questions: List of question strings to visualize
    """
    if not questions:
        print("No questions provided. Exiting...")
        sys.exit(1)
    setup_gui(questions)
