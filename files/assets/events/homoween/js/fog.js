canvasWidth = 1600;
canvasHeight = 200;

pCount = 0;


pCollection = new Array();

let puffs = 1;
let particlesPerPuff = 1000;
let img = `${SITE_FULL_IMAGES}/assets/events/homoween/images/smoke.webp`;

let smokeImage = new Image();
smokeImage.src = img;

for (let i1 = 0 ; i1 < puffs; i1++)
{
	let puffDelay = i1 * 1500; //300 ms between puffs

	for (let i2 = 0 ; i2 < particlesPerPuff; i2++)
	{
		addNewParticle((i2*50) + puffDelay);
	}
}


draw_fog(new Date().getTime(), 3000)



function addNewParticle(delay)
{

	let p = {};
	p.top = canvasHeight;
	p.left = randBetween(-200,800);

	p.start = new Date().getTime() + delay;
	p.life = 16000;
	p.speedUp = 30;


	p.speedRight = randBetween(0,20);

	p.rot = randBetween(-1,1);
	p.red = Math.floor(randBetween(0,255));
	p.blue = Math.floor(randBetween(0,255));
	p.green = Math.floor(randBetween(0,255));


	p.startOpacity = .3
	p.newTop = p.top;
	p.newLeft = p.left;
	p.size = 200;
	p.growth = 10;

	pCollection[pCount] = p;
	pCount++;


}

function draw_fog(startT, totalT)
{
	//Timing
	let timeDelta = new Date().getTime() - startT;
	let stillAlive = false;

	//Grab and clear the canvas
	let c = document.getElementById("fog-effect");
	let ctx = c.getContext("2d");
	ctx.clearRect(0, 0, c.width, c.height);
	c.width = c.width;

	//Loop through particles
	for (let i= 0; i < pCount; i++)
	{
		//Grab the particle
		let p = pCollection[i];

		//Timing
		let td = new Date().getTime() - p.start;
		let frac = td/p.life

		if (td > 0)
		{
			if (td <= p.life )
			{ stillAlive = true; }

			//attributes that change over time
			let newTop = p.top - (p.speedUp * (td/1000));
			let newLeft = p.left + (p.speedRight * (td/1000));
			let newOpacity = Math.max(p.startOpacity * (1-frac),0);

			let newSize = p.size + (p.growth * (td/1000));
			p.newTop = newTop;
			p.newLeft = newLeft;

			//Draw!
			ctx.fillStyle = 'rgba(150,150,150,' + newOpacity + ')';
			ctx.globalAlpha  = newOpacity;
			ctx.drawImage(smokeImage, newLeft, newTop, newSize, newSize);
		}
	}



	//Repeat if there's still a living particle
	if (stillAlive)
	{
		requestAnimationFrame(function(){draw_fog(startT,totalT);});
	}
	else
	{
		clog(timeDelta + ": stopped");
	}
}

function randBetween(n1,n2)
{
	let r = (Math.random() * (n2 - n1)) + n1;
	return r;
}

function randOffset(n, variance)
{
	//e.g. variance could be 0.1 to go between 0.9 and 1.1
	let max = 1 + variance;
	let min = 1 - variance;
	let r = Math.random() * (max - min) + min;
	return n * r;
}

function clog(s)
{
	console.log(s);
}
