class ClusterMenu extends React.Component
  constructor: (@props) ->
    @state = clusters: [
      name: 'local'
      host: document.domain
      port: location.port
    ]
    super @props

  click: ->
    dropdownNode = ReactDOM.findDOMNode @refs.dropdown
    $(dropdownNode).dropdown()

  render: ->
    settings =
      crossDomain: true
      url: "http://#{document.domain}:#{location.port}/clusters"
      method: 'GET'
    # $.ajax(settings).done (response) ->
    #   console.log response

    <div className='ui dropdown item' onClick={@click.bind @}
      ref='dropdown'>
      Cluster
      <i className='dropdown icon'></i>
      <div className='menu'>
        {<ClusterItem {...cluster}/> for cluster in @state.clusters}
      </div>
    </div>

class ClusterItem extends React.Component
  select: ->
    console.log "selected #{@props.name}"

  render: ->
    <div onClick={@select.bind @} className='item'>
      {@props.name} <div className="ui small basic label">
        {@props.host}:{@props.port} </div>
    </div>

ReactDOM.render <ClusterMenu/>, document.getElementById 'clusters'
