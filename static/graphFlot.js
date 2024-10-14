function updateGraph(dateString) {
	const urlDate='/' + dateString.replace(/-/g, '') + '/graphdata'
	
	$.ajax({
		url: urlDate,
		type: 'GET',
		dataType: 'json',
		success: function(data) {
			//plot
			$(document).ready(function () {

				const options = {
					xaxes: [
						{ mode: "time" }
					],
					yaxes: [
						{ position: 'left', axisLabel: 'Temp (C)', showTickLabels: 'none', show: true },
						{ position: 'right', axisLabel: 'On/Off', show: true, showTickLabels: 'none', showTicks: false, gridLines: false }
					]
				};

				var indices = []
				var fdata = []
				
				indices = [0,1,2,3];
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				fdata[0].yaxis=1;
				fdata[1].yaxis=1;
				fdata[2].yaxis=1;
				fdata[3].yaxis=2;
				$.plot( $("#mainplot"),fdata,options);

				indices = [4,5,6,7];
				fdata = []
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				fdata[0].yaxis=1;
				fdata[1].yaxis=1;
				fdata[2].yaxis=1;
				fdata[3].yaxis=2;
				$.plot( $("#upstairplot"),fdata,options);

				indices = [8,9,10,11];
				fdata = []
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				fdata[0].yaxis=1;
				fdata[1].yaxis=1;
				fdata[2].yaxis=1;
				fdata[3].yaxis=2;
				$.plot( $("#garageplot"),fdata,options);

				options.yaxes[1].show=false;

				indices = [12];
				fdata = []
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				$.plot( $("#outtempplot"),fdata,options);
				
				indices = [13,14];
				fdata = []
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				$.plot( $("#watertempplot"),fdata,options);
				
				indices = [15,16];
				fdata = []
				fdata = data.filter(function(obj, index) {
					return indices.includes(index);
				});
				$.plot( $("#waterdtplot"),fdata,options);
				
			});
		}
	});
}