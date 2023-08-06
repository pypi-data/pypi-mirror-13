/**
 * Created by fserena on 3/06/15.
 */

$(function () { // on dom ready

    var cy = cytoscape({
        container: document.getElementById('cy'),

        style: cytoscape.stylesheet()
            .selector('node')
            .css({
                'content': 'data(label)',
                'color': '#484849',
                'shape': 'data(shape)',
                'width': 'mapData(width, 1, 200, 1, 200)',
                'height': '40',
                'text-valign': 'center',
                'background-color': 'white',
                'background-opacity': 0.2,
                'font-weight': 'regular',
                'font-family': 'EagerNaturalist',
                'font-size': '22px'
            })
            .selector('edge')
            .css({
                'target-arrow-shape': 'triangle',
                //'width': 3,
                'line-color': '#484849',
                'target-arrow-color': '#484849',
                'content': 'data(label)',
                'color': '#484849',
                'edge-text-rotation': 'autorotate',
                'text-valign': 'top',
                'text-wrap': 'wrap',
                'curve-style': 'bezier',
                'font-family': 'EagerNaturalist',
                'font-size': '18px'
            }).selector('edge.highlighted')
            .css({
                'transition-property': 'line-color, target-arrow-color, color, border-width, shadow-color, visibility',
                'transition-duration': '0.8s',
                'visibility': 'visible'
            }).selector('node.highlighted')
            .css({
                'transition-property': 'background-color, line-color, target-arrow-color, color, border-width, shadow-color, visibility',
                'transition-duration': '0.8s',
                'color': '#484849',
                'border-width': 2,
                'border-opacity': 0.7,
                'font-weight': 'regular',
                'shadow-color': '#484849',
                'shadow-opacity': 0.5,
                'shadow-offset-x': 0,
                'shadow-offset-y': 0,
                'shadow-blur': 2,
                'visibility': 'visible'
            }).selector('edge.subclass')
            .css({
                'line-style': 'dashed',
                'source-arrow-shape': 'triangle',
                'source-arrow-fill': 'hollow',
                'target-arrow-shape': 'none'
            }).selector('node.seed')
            .css({
                'border-color': '#0078B6',
                'shadow-color': '#0078B6',
                'visibility': 'visible',
                'color': '#0078B6'
            }).selector('edge.end')
            .css({
                'line-color': '#1F8A1F',
                'color': '#1F8A1F',
                'target-arrow-color': '#1F8A1F',
                'text-shadow-color': '#1F8A1F',
                'text-shadow-opacity': 0.1,
                'text-shadow-offset-x': 0,
                'text-shadow-offset-y': 0,
                'text-shadow-blur': 2
            }).selector('node.end')
            .css({
                'border-color': '#1F8A1F',
                'shadow-color': '#1F8A1F',
                'color': '#1F8A1F'
            }),

        elements: {
            nodes: vGraph.nodes,
            edges: vGraph.edges
        }
    });

    var options = {
        name: 'arbor',

        animate: true, // whether to show the layout as it's running
        maxSimulationTime: 4000, // max length in ms to run the layout
        fit: false, // on every layout reposition of nodes, fit the viewport
        padding: 30, // padding around the simulation
        boundingBox: undefined, //{x1: 0, y1: 0, w: 1000, h: 1000}, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
        ungrabifyWhileSimulating: false, // so you can't drag nodes during layout

        // callbacks on layout events
        ready: undefined, // callback on layoutready
        stop: undefined, // callback on layoutstop

        // forces used by arbor (use arbor default on undefined)
        repulsion: 2000,
        stiffness: undefined,
        friction: 0.9,
        gravity: true,
        fps: undefined,
        precision: 0.9,

        // static numbers or functions that dynamically return what these
        // values should be for each element
        // e.g. nodeMass: function(n){ return n.data('weight') }
        nodeMass: undefined,
        edgeLength: undefined,

        stepSize: 0.2, // smoothing of arbor bounding box

        // function that returns true if the system is stable to indicate
        // that the layout can be stopped
        stableEnergy: function (energy) {
            var e = energy;
            return (e.max <= 0.5) || (e.mean <= 0.3);
        },

        // infinite layout options
        infinite: true // overrides all other options for a forces-all-the-time mode
    };

    cy.layout(options);

    cy.bfs = [];

    vGraph.roots.forEach(function (r, index) {
        cy.bfs.push(
            {
                index: index,
                bfs: cy.elements().bfs('#' + vGraph.roots[index], function () {
                }, true)
            }
        );
    });

    var highlightNextEle = function (b) {
        b.bfs.path[b.index].addClass('highlighted');

        if (b.index < b.bfs.path.length) {
            b.index++;
            setTimeout(function () {
                highlightNextEle(b);
            }, 200);
        }
    };

    // kick off first highlights
    cy.bfs.forEach(function (b) {
        highlightNextEle(b);
    });


}); // on dom ready