---
hide:
  - toc
---

# 🌳 Schema Interactive Tree

<style>
/* 3-Pane Layout */
.schema-explorer {
    display: flex;
    height: 80vh;
    border: 1px solid var(--md-default-fg-color--lightest);
    border-radius: 8px;
    overflow: hidden;
    background: var(--md-default-bg-color);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Left Pane: Tree View */
.pane-left {
    width: 250px;
    min-width: 200px;
    border-right: 1px solid var(--md-default-fg-color--lightest);
    overflow-y: auto;
    padding: 10px;
    background: var(--md-default-bg-color);
    resize: horizontal;
}
.tree-nav ul {
    list-style-type: none;
    padding-left: 15px;
    margin: 0;
}
.tree-nav > ul { padding-left: 0; }
.tree-nav li {
    margin: 4px 0;
    font-size: 0.9em;
    cursor: pointer;
    white-space: nowrap;
}
.tree-nav li .node-name {
    color: var(--md-typeset-a-color);
}
.tree-nav li.selected > .node-name {
    font-weight: bold;
    background: var(--md-primary-fg-color--light);
    color: white;
    padding: 2px 4px;
    border-radius: 4px;
}

/* Center Pane: D3 Graph */
.pane-center {
    flex-grow: 1;
    position: relative;
    overflow: hidden;
    background: var(--md-code-bg-color); /* Light gray for contrast */
}

/* Right Pane: Details */
.pane-right {
    width: 350px;
    min-width: 250px;
    border-left: 1px solid var(--md-default-fg-color--lightest);
    overflow-y: auto;
    padding: 20px;
    background: var(--md-default-bg-color);
}

.details-title {
    font-size: 1.5em;
    font-weight: bold;
    color: var(--md-primary-fg-color);
    margin-top: 0;
    margin-bottom: 10px;
    border-bottom: 2px solid var(--md-primary-fg-color);
    padding-bottom: 5px;
}
.badges {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}
.badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
}
.badge-type { background: #e3f2fd; color: #1565c0; }
.badge-cardinality { background: #fbe9e7; color: #d84315; }
.details-desc {
    font-size: 0.95em;
    line-height: 1.5;
    margin-bottom: 20px;
}

/* D3 Graph Styles */
.node rect {
    fill: var(--md-default-bg-color);
    stroke: var(--md-primary-fg-color);
    stroke-width: 1.5px;
    rx: 4px;
    cursor: pointer;
}
.node text {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
}
.node .name { font-weight: bold; fill: var(--md-typeset-color); }
.node .type { fill: #1565c0; font-size: 10px; }
.node .cardinality { fill: #d84315; font-size: 10px; text-anchor: end; }
.node .expand-btn { fill: #fff; stroke: var(--md-primary-fg-color); stroke-width: 1px; cursor: pointer; }
.node .expand-text { fill: var(--md-primary-fg-color); font-size: 10px; text-anchor: middle; cursor: pointer; font-family: monospace; }
.link {
    fill: none;
    stroke: #ccc;
    stroke-width: 1.5px;
}

.rule-card {
    background: #fff3e0;
    border-left: 4px solid #ff9800;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 0 4px 4px 0;
    font-size: 0.85em;
}
.rule-error { background: #ffebee; border-left-color: #f44336; }
</style>

<div class="schema-explorer">
    <div class="pane-left" id="tree-nav">
        <!-- Vertical tree list -->
    </div>
    
    <div class="pane-center" id="d3-graph">
        <!-- SVG Canvas -->
    </div>
    
    <div class="pane-right" id="details-panel">
        <div class="details-title">Select an element</div>
        <div class="details-desc">Click on any node in the center graph or left tree to view its details, description, and validation rules.</div>
    </div>
</div>

<!-- Load D3.js -->
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    let globalData = null;
    let selectedNode = null;

    // Fetch data
    fetch("../schema_data/schema.json")
        .then(response => {
            if (!response.ok) throw new Error("HTTP error " + response.status);
            return response.json();
        })
        .then(data => {
            globalData = data;
            initNavTree(data);
            initD3Graph(data);
            selectNode(data); // select root by default
        })
        .catch(err => {
            console.error("Error loading schema:", err);
            document.getElementById("d3-graph").innerHTML = `<div style="color:red; padding:20px;">Failed to load schema data. Check console.</div>`;
        });

    // ==========================================
    // RIGHT PANE: DETAILS
    // ==========================================
    function selectNode(d) {
        // d might be raw data or d3 hierarchy node. Normalize to raw data.
        const data = d.data || d;
        selectedNode = data;
        
        // Update DOM
        const panel = document.getElementById("details-panel");
        let html = `<div class="details-title">${data.name || 'Unnamed Element'}</div>`;
        html += `<div class="badges">`;
        if (data.type) html += `<span class="badge badge-type">Type: ${data.type}</span>`;
        if (data.cardinality) html += `<span class="badge badge-cardinality">Cardinality: ${data.cardinality}</span>`;
        html += `</div>`;
        
        html += `<div class="details-desc">${data.description || '<i>No description available.</i>'}</div>`;
        
        // Attributes
        if (data.attributes && data.attributes.length > 0) {
            html += `<h3>Attributes</h3><ul>`;
            data.attributes.forEach(attr => {
                html += `<li><strong>@${attr.name}</strong>: ${attr.type} (${attr.use})<br><i>${attr.description}</i></li>`;
            });
            html += `</ul>`;
        }

        // Rules
        if (data.rules && data.rules.length > 0) {
            html += `<h3>Business Rules</h3>`;
            data.rules.forEach(rule => {
                const roleClass = rule.role === 'error' ? 'rule-error' : '';
                html += `<div class="rule-card ${roleClass}">
                    <strong>[${rule.id}]</strong> ${rule.description}
                </div>`;
            });
        }
        
        panel.innerHTML = html;
        
        // Highlight in left nav
        document.querySelectorAll('.tree-nav li').forEach(li => li.classList.remove('selected'));
        const navEl = document.getElementById(`nav-${data.name}`);
        if(navEl) navEl.classList.add('selected');
    }

    // ==========================================
    // LEFT PANE: NAV TREE
    // ==========================================
    function initNavTree(data) {
        const container = document.getElementById("tree-nav");
        const nav = document.createElement('div');
        nav.className = "tree-nav";
        
        function buildUL(nodeData) {
            const ul = document.createElement('ul');
            const li = document.createElement('li');
            li.id = `nav-${nodeData.name}`;
            
            const span = document.createElement('span');
            span.className = 'node-name';
            span.innerText = nodeData.name + (nodeData.cardinality ? ` ${nodeData.cardinality}` : '');
            span.onclick = (e) => {
                e.stopPropagation();
                selectNode(nodeData);
            };
            li.appendChild(span);
            
            if (nodeData.children && nodeData.children.length > 0) {
                const childUl = document.createElement('ul');
                nodeData.children.forEach(child => {
                    childUl.appendChild(buildUL(child).firstChild); // append the li
                });
                li.appendChild(childUl);
            }
            ul.appendChild(li);
            return ul;
        }
        
        nav.appendChild(buildUL(data));
        container.appendChild(nav);
    }

    // ==========================================
    // CENTER PANE: D3 GRAPH
    // ==========================================
    function initD3Graph(data) {
        const container = document.getElementById("d3-graph");
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        const margin = {top: 20, right: 90, bottom: 30, left: 90};
        const dx = 50; // vertical spacing
        const dy = 250; // horizontal spacing
        const nodeWidth = 220;
        const nodeHeight = 60;
        
        const svg = d3.select("#d3-graph").append("svg")
            .attr("width", width)
            .attr("height", height)
            .style("cursor", "grab");
            
        const g = svg.append("g");
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
        svg.call(zoom).on("dblclick.zoom", null);
        
        // Center the root node
        const initialTransform = d3.zoomIdentity.translate(50, height/2).scale(0.8);
        svg.call(zoom.transform, initialTransform);
        
        const tree = d3.tree().nodeSize([dx + nodeHeight, dy]);
        
        const root = d3.hierarchy(data);
        root.x0 = 0;
        root.y0 = 0;
        
        // Collapse all children of root by default to keep it tidy
        if (root.children) {
            root.children.forEach(collapse);
        }
        
        function collapse(d) {
            if (d.children) {
                d._children = d.children;
                d._children.forEach(collapse);
                d.children = null;
            }
        }
        
        update(root);
        
        function update(source) {
            const treeData = tree(root);
            const nodes = treeData.descendants();
            const links = treeData.links();
            
            // Normalize for fixed-depth
            nodes.forEach(d => { d.y = d.depth * dy; });
            
            let i = 0;
            const node = g.selectAll("g.node")
                .data(nodes, d => d.id || (d.id = ++i));
                
            // Enter any new nodes at the parent's previous position.
            const nodeEnter = node.enter().append("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${source.y0},${source.x0})`)
                .on("click", (event, d) => {
                    selectNode(d);
                });
                
            // Draw Box
            nodeEnter.append("rect")
                .attr("width", nodeWidth)
                .attr("height", nodeHeight)
                .attr("y", -nodeHeight/2)
                .attr("x", 0);
                
            // Text: Name
            nodeEnter.append("text")
                .attr("class", "name")
                .attr("x", 10)
                .attr("y", -10)
                .text(d => d.data.name.length > 25 ? d.data.name.substring(0, 22) + '...' : d.data.name);
                
            // Text: Type
            nodeEnter.append("text")
                .attr("class", "type")
                .attr("x", 10)
                .attr("y", 10)
                .text(d => d.data.type);
                
            // Text: Cardinality
            nodeEnter.append("text")
                .attr("class", "cardinality")
                .attr("x", nodeWidth - 10)
                .attr("y", -10)
                .text(d => d.data.cardinality);
                
            // Expand Button (only if has children)
            const btnGroup = nodeEnter.append("g")
                .attr("transform", `translate(${nodeWidth}, 0)`)
                .style("display", d => (d.children || d._children) ? "block" : "none")
                .on("click", (event, d) => {
                    event.stopPropagation();
                    if (d.children) {
                        d._children = d.children;
                        d.children = null;
                    } else {
                        d.children = d._children;
                        d._children = null;
                    }
                    update(d);
                });
                
            btnGroup.append("rect")
                .attr("class", "expand-btn")
                .attr("width", 16)
                .attr("height", 16)
                .attr("y", -8)
                .attr("x", -8)
                .attr("rx", 3);
                
            btnGroup.append("text")
                .attr("class", "expand-text")
                .attr("y", 3)
                .text(d => d._children ? "+" : "-");
            
            // Transition nodes to their new position.
            const nodeUpdate = nodeEnter.merge(node);
            
            nodeUpdate.transition()
                .duration(300)
                .attr("transform", d => `translate(${d.y},${d.x})`);
                
            // Update the button symbol
            nodeUpdate.select(".expand-text")
                .text(d => d._children ? "+" : "-");
            
            // Transition exiting nodes to the parent's new position.
            const nodeExit = node.exit().transition()
                .duration(300)
                .attr("transform", d => `translate(${source.y},${source.x})`)
                .remove();
                
            // Links
            const link = g.selectAll("path.link")
                .data(links, d => d.target.id);
                
            const linkEnter = link.enter().insert("path", "g")
                .attr("class", "link")
                .attr("d", d => {
                    const o = {x: source.x0, y: source.y0};
                    return diagonal(o, o);
                });
                
            const linkUpdate = linkEnter.merge(link);
            
            linkUpdate.transition()
                .duration(300)
                .attr("d", d => diagonal(d.source, d.target));
                
            link.exit().transition()
                .duration(300)
                .attr("d", d => {
                    const o = {x: source.x, y: source.y};
                    return diagonal(o, o);
                })
                .remove();
                
            nodes.forEach(d => {
                d.x0 = d.x;
                d.y0 = d.y;
            });
        }
        
        function diagonal(s, d) {
            return `M ${s.y + nodeWidth} ${s.x}
                    C ${(s.y + nodeWidth + d.y) / 2} ${s.x},
                      ${(s.y + nodeWidth + d.y) / 2} ${d.x},
                      ${d.y} ${d.x}`;
        }
    }
});
</script>
