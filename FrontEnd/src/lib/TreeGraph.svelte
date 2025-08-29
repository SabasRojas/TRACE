<script>
  import { onMount } from 'svelte';
  import { select, hierarchy, tree, linkVertical, zoom } from 'd3';

  export let data;
  let container;
  let width = 900;
  let height = 600;

  onMount(() => {
    if (!data || !Array.isArray(data.children) || data.children.length === 0) {
      console.warn('Empty tree passed to TreeGraph:', data);
      return;
    }

    console.log("Rendering tree with data:", data);

    const root = hierarchy(data);
    const layout = tree().size([width, height - 100]);
    layout(root);

    const svg = select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g');

    svg.call(
      zoom().on('zoom', (event) => {
        g.attr('transform', event.transform);
      })
    );

    // Links
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', linkVertical().x(d => d.x).y(d => d.y));

    // Nodes
    const node = g.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.x},${d.y})`);

    // Node background (severity colored)
    node.append('rect')
      .attr('width', 150)
      .attr('height', 60)
      .attr('x', -75)
      .attr('y', -30)
      .attr('rx', 10)
      .attr('ry', 10)
      .attr('fill', d => {
        const sev = d.data.severity;
        if (sev === 'high') return '#fee2e2';
        if (sev === 'medium') return '#fef9c3';
        if (sev === 'low') return '#d1fae5';
        return '#f3f4f6';
      });

    // Node title
    node.append('text')
      .attr('dy', '-0.3em')
      .attr('text-anchor', 'middle')
      .text(d => d.data.name)
      .style('font-weight', '600');

    // Severity label
    node.append('text')
      .attr('dy', '1.1em')
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#6b7280')
      .text(d => {
        const sev = d.data.severity;
        return sev ? sev.charAt(0).toUpperCase() + sev.slice(1) : '';
      });
  });
</script>

<div bind:this={container}></div>

<style>
  div {
    /* Center the tree graph */
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    padding: 1rem;
  }

  :global(svg) {
    background-color: white;
    border-radius: 1rem;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
    max-width: 100%;
  }

  :global(.link) {
    fill: none;
    stroke: #60a5fa;
    stroke-width: 2;
  }

  :global(.node rect) {
    stroke: #cbd5e1;
    stroke-width: 1;
    filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.1));
  }

  :global(.node text) {
    font-family: 'Segoe UI', sans-serif;
    pointer-events: none;
    fill: #111827;
  }
</style>
