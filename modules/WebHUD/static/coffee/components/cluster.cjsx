$ = jQuery = require 'jquery'
React = require 'react'


class ClusterMenu extends React.Component
  constructor: (@props) ->
    @state = clusters: [
      name: 'local'
      host: document.domain
      port: location.port
    ], loading: yes

    @click = @click.bind @
    super @props

  click: ->
    $(@refs.dropdown).dropdown()

  refresh: ->
    settings =
      crossDomain: true
      url: "http://#{document.domain}:#{location.port}/clusters"
      method: 'GET'
    $.ajax(settings).done (response) =>
      nClusters = @state.clusters
      nClusters.splice(1) # keep only the first entry
      for k, v of response
        nClusters.append
          name: v.name
          host: v.host
          port: v.port
      @setState loading: no, clusters: nClusters

  componentDidMount: -> @refresh()

  render: ->
    loading = @state.loading

    <div className="ui#{if loading then ' loading' else ''} floating dropdown
      item" onClick={@click} ref='dropdown'>
      Cluster
      <i className='dropdown icon'/>
      <div className='menu' style={minWidth: 'calc(200%)'}>
        {for cluster in @state.clusters
          <ClusterItem key={cluster.name} {...cluster}/>}
      </div>
    </div>


class ClusterItem extends React.Component
  constructor: (@props) ->
    @select = @select.bind @
    super @props

  select: ->
    console.log "selected #{@props.name}"

  render: ->
    <div onClick={@select} className='item'>
      {@props.name}
      <span className='description'>{@props.host}:{@props.port}</span>
    </div>


module.exports = ClusterMenu: ClusterMenu
