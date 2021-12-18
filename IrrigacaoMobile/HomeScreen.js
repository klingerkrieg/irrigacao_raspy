import * as React from 'react';
import { View, ScrollView, SafeAreaView, RefreshControl, StyleSheet, Text } from 'react-native';
var data = require("./Data")


const styles = StyleSheet.create({
    container: {
     flex: 1,
     paddingTop: 22
    },
    valve: {
      borderTopWidth:2
    },
    item: {
      padding: 10,
      fontSize: 18,
      height: 44,
    },
  });


var listKeys = 0;


const ListItem = (props) => {
    return <View >
        <Text style={styles.item} >
        <Text style={{ fontWeight:"bold" }}>{props.label}:</Text>
        {props.value}</Text>
    </View>
  }
  
  
  class HomeScreen extends React.Component {
  
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            refreshing: true,
        }
    }
  
    /*componentDidMount() {
        this.fetchConf();
    }*/
  
    fetchConf() {
        this.setState({ refreshing: true });
        fetch('http://'+data.IP+':8080/')
            .then(res => res.text())
            .then(resText => resText.replace(/'/g, '"'))
            .then(resJson => {
                console.log(resJson)
                data.configData = JSON.parse(resJson)
                this.setState({ data: data.configData });
                this.setState({ refreshing: false });
            }).catch(e => console.log(e));
    }
  
    handleRefresh = () => {
        this.setState({ refreshing: false }, () => { this.fetchConf() }); // call fetchCats after setting the state
    }


    componentDidMount() {
        this.fetchConf();
        this.interval = setInterval(() => { this.fetchConf() }, 15000);
    }
    componentWillUnmount() {
        clearInterval(this.interval);
    }
  
  
    render() {
    
      return (
        <SafeAreaView style={styles.container}>
          <ScrollView
            contentContainerStyle={styles.scrollView}
            refreshControl={
              <RefreshControl
                refreshing={this.state.refreshing}
                onRefresh={this.handleRefresh.bind(this)}
              />
            }>
  
              <ListItem key={listKeys++} label="Dia" value={this.state.data.last_day} ></ListItem>
              <ListItem key={listKeys++} label="Hora" value={this.state.data.current_time} ></ListItem>
              <ListItem key={listKeys++} label="Chuva hoje" value={this.state.data.precipitation_today} ></ListItem>
              <ListItem key={listKeys++} label="Chuva nas próximas horas" value={this.state.data.next_precipitation} ></ListItem>
              <ListItem key={listKeys++} label="Limite de chuva para ativação" value={this.state.data.precipitation_limit} ></ListItem>
              
              
  
              {this.state.data.valves != undefined &&
              this.state.data.valves.map(function(valve, i){
                  return (
                        <View key={listKeys++} style={styles.valve}>
  
                        <ListItem label="Nome" value={valve.name} ></ListItem>
                        <ListItem label="Status" value={valve.irrigation} ></ListItem>
                        <ListItem label="Duração agendada" value={valve.duration} ></ListItem>
                        <ListItem label="Agendamento" value={valve.scheduled_time} ></ListItem>
                        <ListItem label="GPIO" value={valve.gpio} ></ListItem>
                        <ListItem label="Tempo que falta" value={valve.remains} ></ListItem>
                        <ListItem label="Tempo irrigado" value={valve.irrigated} ></ListItem>
                        
                        </View>
                        )
              })}
  
               
          </ScrollView>
        </SafeAreaView>)
    }
  }

  export default HomeScreen;