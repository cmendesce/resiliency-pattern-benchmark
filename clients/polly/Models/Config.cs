﻿namespace ResiliencePatterns.Polly.Controllers
{
    public class Config<P> where P : class
    {
        public int MaxRequestsAllowed { get; set; }
        public int TargetSuccessfulRequests { get; set; }

        public P Params { get; set; }
    }
}
