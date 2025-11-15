"""
AWS Bedrock AI Service for generating stock recommendations
"""
import boto3
import json
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered stock analysis using AWS Bedrock"""

    def __init__(self):
        self.bedrock_available = False
        try:
            # Initialize Bedrock client
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            self.bedrock_available = True
            logger.info("AWS Bedrock client initialized successfully")
        except Exception as e:
            logger.warning(f"AWS Bedrock not available: {str(e)}")
            self.bedrock = None

    def generate_summary(self, symbol: str, analysis: dict) -> str:
        """
        Generate AI-powered stock analysis summary
        Falls back to rule-based summary if Bedrock is not available
        """
        if self.bedrock_available and self.bedrock:
            try:
                return self._generate_bedrock_summary(symbol, analysis)
            except Exception as e:
                logger.error(f"Bedrock error: {str(e)}, falling back to rule-based summary")
                return self._generate_rule_based_summary(symbol, analysis)
        else:
            return self._generate_rule_based_summary(symbol, analysis)

    def _generate_bedrock_summary(self, symbol: str, analysis: dict) -> str:
        """Generate summary using AWS Bedrock"""
        try:
            rsi = analysis.get('rsi', 50)
            macd = analysis.get('macd', 0)
            trend = analysis.get('trend', 'Neutral')
            recommendation = analysis.get('recommendation', 'Hold')
            price_change_percent = analysis.get('price_change_percent', 0)

            prompt = f"""Analyze the following stock indicators for {symbol}:

Technical Indicators:
- RSI (Relative Strength Index): {rsi:.2f}
- MACD: {macd:.4f}
- Current Trend: {trend}
- Price Change: {price_change_percent:.2f}%
- EMA 12: {analysis.get('ema_12', 0):.2f}
- EMA 50: {analysis.get('ema_50', 0):.2f}

Current Recommendation: {recommendation}

Provide a concise 2-3 sentence analysis of the stock's current technical position and justify the {recommendation} recommendation. Focus on the key indicators and trend."""

            # Bedrock request body for Titan model
            body = json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 200,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            })

            response = self.bedrock.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response['body'].read())
            summary = response_body.get('results', [{}])[0].get('outputText', '').strip()

            if summary:
                return summary
            else:
                raise Exception("Empty response from Bedrock")

        except Exception as e:
            logger.error(f"Error generating Bedrock summary: {str(e)}")
            raise

    def _generate_rule_based_summary(self, symbol: str, analysis: dict) -> str:
        """Generate rule-based summary when AI is not available"""
        try:
            rsi = analysis.get('rsi', 50)
            macd = analysis.get('macd', 0)
            trend = analysis.get('trend', 'Neutral')
            recommendation = analysis.get('recommendation', 'Hold')
            price_change_percent = analysis.get('price_change_percent', 0)
            ema_12 = analysis.get('ema_12', 0)
            ema_50 = analysis.get('ema_50', 0)

            # Build summary based on indicators
            summary_parts = []

            # Trend analysis
            if trend == "Bullish":
                summary_parts.append(f"{symbol} shows a bullish trend")
            elif trend == "Bearish":
                summary_parts.append(f"{symbol} shows a bearish trend")
            else:
                summary_parts.append(f"{symbol} is in a neutral trend")

            # Price movement
            if price_change_percent > 2:
                summary_parts.append(f"with strong upward momentum ({price_change_percent:+.2f}%)")
            elif price_change_percent < -2:
                summary_parts.append(f"with downward pressure ({price_change_percent:+.2f}%)")
            else:
                summary_parts.append(f"with moderate price action ({price_change_percent:+.2f}%)")

            # RSI analysis
            if rsi < 30:
                rsi_signal = "RSI indicates oversold conditions, suggesting a potential buying opportunity"
            elif rsi > 70:
                rsi_signal = "RSI shows overbought levels, exercise caution on new positions"
            elif rsi > 50:
                rsi_signal = "RSI is in neutral-to-bullish territory"
            else:
                rsi_signal = "RSI suggests neutral momentum"

            summary_parts.append(f". {rsi_signal}")

            # MACD analysis
            if macd > 0.5:
                macd_signal = "Strong positive MACD supports the bullish case"
            elif macd < -0.5:
                macd_signal = "Negative MACD indicates bearish momentum"
            elif macd > 0:
                macd_signal = "Positive MACD suggests upward momentum"
            else:
                macd_signal = "MACD shows mixed signals"

            summary_parts.append(f". {macd_signal}")

            # EMA crossover
            if ema_12 > ema_50:
                ema_signal = "Short-term EMA is above long-term EMA, confirming uptrend"
            else:
                ema_signal = "Short-term EMA below long-term EMA suggests caution"

            summary_parts.append(f". {ema_signal}")

            # Final recommendation
            rec_map = {
                'Buy': 'This technical setup favors accumulation',
                'Sell': 'Consider reducing exposure or taking profits',
                'Hold': 'Maintain current positions and monitor for clearer signals'
            }
            summary_parts.append(f". {rec_map.get(recommendation, 'Monitor the situation closely')}.")

            return ''.join(summary_parts)

        except Exception as e:
            logger.error(f"Error generating rule-based summary: {str(e)}")
            return f"{recommendation} - Technical analysis complete. Monitor key support and resistance levels."

    def calculate_confidence_score(self, analysis: dict) -> float:
        """
        Calculate confidence score (0-100) based on indicator alignment
        """
        try:
            rsi = analysis.get('rsi', 50)
            macd = analysis.get('macd', 0)
            trend = analysis.get('trend', 'Neutral')
            recommendation = analysis.get('recommendation', 'Hold')

            score = 50.0  # Base score

            # RSI contribution
            if recommendation == 'Buy':
                if rsi < 35:
                    score += 15
                elif rsi < 45:
                    score += 10
            elif recommendation == 'Sell':
                if rsi > 65:
                    score += 15
                elif rsi > 55:
                    score += 10

            # MACD contribution
            if recommendation == 'Buy' and macd > 0:
                score += 15
            elif recommendation == 'Sell' and macd < 0:
                score += 15
            elif recommendation == 'Hold':
                score += 10

            # Trend alignment
            if (recommendation == 'Buy' and trend == 'Bullish') or \
               (recommendation == 'Sell' and trend == 'Bearish') or \
               (recommendation == 'Hold' and trend == 'Neutral'):
                score += 20

            return min(100.0, max(0.0, score))

        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 50.0
