class ClusterMenu extends React.Component
  constructor: (@props) ->
    @state = clusters: [
      name: 'local'
      host: document.domain
      port: location.port
    ], loading: yes
    super @props

  click: ->
    dropdownNode = ReactDOM.findDOMNode @refs.dropdown
    $(dropdownNode).dropdown()

  refresh: ->
    settings =
      crossDomain: true
      url: "http://#{document.domain}:#{location.port}/clusters"
      method: 'GET'
    $.ajax(settings).done (response) =>
      console.log response
      @setState loading: no

  componentDidMount: -> @refresh()

  render: ->
    loading = @state.loading

    <div className="ui#{if loading then ' loading' else ''} floating dropdown
      item" onClick={@click.bind @} ref='dropdown'>
      Cluster
      <i className='dropdown icon'/>
      <div className='menu' style={'min-width': 'calc(200%)'}>
        {<ClusterItem {...cluster}/> for cluster in @state.clusters}
      </div>
    </div>

class ClusterItem extends React.Component
  select: ->
    console.log "selected #{@props.name}"

  render: ->
    <div onClick={@select.bind @} className='item'>
      {@props.name}
      <span className='description'>{@props.host}:{@props.port}</span>
    </div>

ReactDOM.render <ClusterMenu/>, document.getElementById 'clusters'
