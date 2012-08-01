{% block content %}
<div id="settings">

    <div id="tabs">
        <ul>
            <li><a href="#rulenames">Rule Names</a></li>
            <li><a href="#blacklists">Blacklists</a></li>
        </ul>
        
        <div id="rulenames">
            <div class="table">
                <div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
                    <span class="col1">Snort Rule ID</span>
                    <span class="col2">Look Up</span>
                    <span class="col3">Hide</span>
                    <span class="col4">Rule Name</span>
                </div>
            
                {% for rule in rules %}
                    <div class="table-row">
                        <form action="/index.php?page=settings&update=rule&id={{rule.rule}" method="post" name="rule_{{rule.rule}}">
                            <span class="col1">{{rule.rule}</span>
                            <span class="col2"><a class="button" href="http://snortid.com/snortid.asp?QueryId={{rule.rule}}" target="_blank">snortid.com lookup</a></span>
                            <span class="col3"><input type="checkbox" name="hide" {% if rule.hide }}checked="checked"{% endif %} value="1"/></span>
                            <span class="col4">
                                <input type="text" name="rulename" value="{{rule.rule_name}}" />
                                <input class="button" type="submit" value="Update"/>
                            </span>
                        </form>
                    </div>
                {% endfor %}
            </div>
        </div>
        
        <div id="blacklists">
            <div class="table">
                <div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
                    <span class="col1">Blacklist</span>
                    <span class="col2">URL</span>
                    <span class="col3">Last Updated</span>
                    <span class="col4">Hide</span>
                </div>
            
                {% for blacklist in blacklists %}
                    <div class="table-row">
                        <span class="col1">{{blacklist.name}</span>
                        <span class="col2"><a class="button" href="{{blacklist.url}}" target="_blank">{{blacklist.url}}</a></span>
                        <span class="col3">{{blacklist.updated}}</span>
                        <span class="col4">
                            <form action="/index.php?page=settings&update=blacklist&id={{blacklist.pk}}" method="post" name="blacklist_{{blacklist.pk}}">
                                <input type="checkbox" name="hide" {% if blacklist.hide %}checked="checked"{% endif %} value="1"/>
                                <input class="button" type="submit" value="Update"/>
                            </form>
                        </span>
                    </div>
                {% endfor %}
            </div>
        
        </div>
    </div>

</div>
{% endblock content %}
